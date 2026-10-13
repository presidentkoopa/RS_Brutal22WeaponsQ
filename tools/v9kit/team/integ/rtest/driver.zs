// TEST ONLY (team/integ/rtest): loaded as an overlay after a production pack, never shipped.
//
// v9t_mode 1 (fire all): every weapon in the player's slots, on a fixed schedule: switch at
//   T0 + k * v9t_slot, report readiness at +105, fire at +110 / +140 / +170 when ready.
// v9t_mode 2 (reload): the guns in v9t_guns one after another: switch, wait until ready,
//   fire twice (or, with v9t_empty, take the items in v9t_take to 0), reload the way the set
//   does it (BD22: the tokens its Inputs.acs gives for +reload; others: the engine's Reload
//   state), wait until the gun has been ready for 10 tics, print the inventory.
// Recoil log (v9t_hl 1): what RSQ_Hands.ModifyBobLayer3D gives the gun / support hand,
//   called from ui as the renderer does, every frame the gun layer is kicked.
class V9T_Driver : EventHandler
{
	Array<String> guns;
	int step;			// mode 2: index in guns
	int phase;			// mode 2: 0 switch, 1 wait ready, 2 fired, 3 reloading, 4 done
	int phaseTic;
	int readyRun;
	int shots;
	bool listed;

	const T0 = 40;

	clearscope static int CVInt(Name n, int d) { let c = CVar.FindCVar(n); return c ? c.GetInt() : d; }
	clearscope static String CVStr(Name n) { let c = CVar.FindCVar(n); return c ? c.GetString() : ""; }

	override void WorldTick()
	{
		let mo = players[consoleplayer].mo;
		if (!mo)
			return;
		int mode = CVInt('v9t_mode', 0);
		if (mode == 1)
			FireAll(mo);
		else if (mode == 2)
			ReloadSeq(mo);
		else if (mode == 3 && Level.maptime % 50 == 0)
		{
			String s = "";
			int n = 0;
			for (let it = mo.Inv; it; it = it.Inv)
				if (it is 'Weapon')
				{
					s = s .. " " .. it.GetClassName();
					n++;
				}
			Console.Printf("V9T t%d weapons %d:%s", Level.maptime, n, s);
		}
	}

	// ------------------------------------------------------------------ helpers
	static bool Ready(PlayerPawn mo, Weapon w)
	{
		let p = mo.player;
		return p.ReadyWeapon == w && w && (p.WeaponState & WF_WEAPONREADY) && p.PendingWeapon == WP_NOCHANGE;
	}

	static String Inv(Actor mo)
	{
		Array<String> items;
		for (let it = mo.Inv; it; it = it.Inv)
		{
			String n = it.GetClassName();
			if (it is 'Weapon' || n.Left(4) == "RSQ_" || n.Left(4) == "RSR_" || n.Left(5) == "RSVR_" || n.Left(4) == "V9T_")
				continue;
			if (it is 'PowerupGiver' || it is 'Powerup' || it is 'Key' || it is 'Armor' || it is 'Health')
				continue;
			items.Push(String.Format("%s=%d", n, it.Amount));
		}
		// sort (insertion)
		for (int i = 1; i < items.Size(); i++)
		{
			String x = items[i];
			int j = i - 1;
			while (j >= 0 && items[j] > x)
			{
				items[j + 1] = items[j];
				j--;
			}
			items[j + 1] = x;
		}
		String s = "";
		for (int i = 0; i < items.Size(); i++)
			s = s .. " " .. items[i];
		return s;
	}

	static String StateName(PlayerPawn mo)
	{
		let w = mo.player.ReadyWeapon;
		let psp = mo.player.FindPSprite(PSP_WEAPON);
		if (!w || !psp || !psp.CurState)
			return "-";
		static const String lbl[] = { "Ready", "RSR_Wait", "Reload", "Fire", "Select", "Deselect" };
		for (int i = 0; i < lbl.Size(); i++)
		{
			let s = w.FindStateByString(lbl[i]);
			if (s && psp.CurState == s)
				return lbl[i];
		}
		let r = w.FindState("Ready");
		return r ? String.Format("Ready%+d", psp.CurState.DistanceTo(r)) : "?";
	}

	static String Ammo(Weapon w, Actor mo)
	{
		if (!w)
			return "";
		return String.Format("ammo1 %s=%d ammo2 %s=%d",
			w.Ammo1 ? w.Ammo1.GetClassName() : 'none', w.Ammo1 ? w.Ammo1.Amount : -1,
			w.Ammo2 ? w.Ammo2.GetClassName() : 'none', w.Ammo2 ? w.Ammo2.Amount : -1);
	}

	void ListSlots(PlayerPawn mo, out Array<String> res)
	{
		let ws = mo.player.weapons;
		for (int slot = 1; slot <= 10; slot++)
		{
			int s = slot % 10;
			for (int i = 0; i < ws.SlotSize(s); i++)
			{
				class<Weapon> c = ws.GetWeapon(s, i);
				if (c && mo.FindInventory(c) && res.Find(c.GetClassName()) == res.Size())
					res.Push(c.GetClassName());
			}
		}
	}

	// ------------------------------------------------------------------ mode 1
	void FireAll(PlayerPawn mo)
	{
		int now = Level.maptime;
		if (now < T0)
			return;
		if (!listed)
		{
			ListSlots(mo, guns);
			listed = true;
			String all = "";
			for (int i = 0; i < guns.Size(); i++)
				all = all .. " " .. guns[i];
			Console.Printf("V9T guns %d:%s", guns.Size(), all);
		}
		int slot = CVInt('v9t_slot', 200);
		int k = (now - T0) / slot;
		int t = (now - T0) % slot;
		if (k >= guns.Size())
		{
			if (t == 0 && k == guns.Size())
				Console.Printf("V9T done t%d", now);
			return;
		}
		class<Weapon> c = guns[k];
		let w = Weapon(mo.FindInventory(c));
		if (!w)
			return;
		if (t == 0)
		{
			mo.player.PendingWeapon = w;
			Console.Printf("V9T gun %d %s switch t%d", k, guns[k], now);
		}
		else if (t == 105)
			Console.Printf("V9T gun %d %s %s t%d state %s %s", k, guns[k], Ready(mo, w) ? "READY" : "NOTREADY", now, StateName(mo), Ammo(w, mo));
		else if (t == 110 || t == 140 || t == 170)
		{
			if (Ready(mo, w))
			{
				String before = Ammo(w, mo);
				mo.FireWeapon(null);
				Console.Printf("V9T gun %d %s FIRE t%d (%s) -> state %s", k, guns[k], now, before, StateName(mo));
			}
			else
				Console.Printf("V9T gun %d %s cannot fire t%d state %s ready %d", k, guns[k], now, StateName(mo), mo.player.ReadyWeapon == w);
		}
		else if (t == slot - 1)
			Console.Printf("V9T gun %d %s end t%d state %s %s", k, guns[k], now, StateName(mo), Ammo(w, mo));
	}

	// ------------------------------------------------------------------ mode 2
	void ReloadSeq(PlayerPawn mo)
	{
		int now = Level.maptime;
		if (now < T0)
			return;
		if (!listed)
		{
			listed = true;
			CVStr('v9t_guns').Split(guns, " ", TOK_SKIPEMPTY);
			phase = 0;
			step = 0;
		}
		if (step >= guns.Size())
		{
			if (step == guns.Size())
			{
				Console.Printf("V9T done t%d", now);
				step++;
			}
			return;
		}
		class<Weapon> c = guns[step];
		let w = c ? Weapon(mo.FindInventory(c)) : null;
		if (!w)
		{
			Console.Printf("V9T %s: not in the inventory", guns[step]);
			step++;
			return;
		}
		bool rdy = Ready(mo, w);
		readyRun = rdy ? readyRun + 1 : 0;
		int dt = now - phaseTic;
		switch (phase)
		{
		case 0:
			mo.player.PendingWeapon = w;
			phase = 1;
			phaseTic = now;
			break;
		case 1:
			if (readyRun >= 10)
			{
				Console.Printf("V9T %s READY t%d |%s", guns[step], now, Inv(mo));
				shots = 0;
				phase = 2;
				phaseTic = now;
				if (CVInt('v9t_empty', 0))
				{
					Array<String> take;
					String tk = CVStr('v9t_take');
					tk.Replace(",", " ");
					tk.Split(take, " ", TOK_SKIPEMPTY);
					for (int i = 0; i < take.Size(); i++)
					{
						class<Inventory> tc = take[i];
						if (tc)
							mo.TakeInventory(tc, 999999);
					}
					Array<String> give;
					String gv = CVStr('v9t_give');
					gv.Replace(",", " ");
					gv.Split(give, " ", TOK_SKIPEMPTY);
					for (int i = 0; i < give.Size(); i++)
					{
						class<Inventory> gc = give[i];
						if (gc)
							mo.GiveInventory(gc, 1);
					}
					shots = 2;
					Console.Printf("V9T %s EMPTIED t%d |%s", guns[step], now, Inv(mo));
				}
			}
			else if (dt > 300)
				Fail(mo, "never ready");
			break;
		case 2:
			if (shots < 2)
			{
				if (readyRun >= 10)
				{
					mo.FireWeapon(null);
					shots++;
					readyRun = 0;
					phaseTic = now;
				}
				else if (dt > 300)
					Fail(mo, "not ready to fire");
				break;
			}
			if (readyRun >= 10)
			{
				Console.Printf("V9T %s FIRED t%d |%s", guns[step], now, Inv(mo));
				Reload(mo, w);
				phase = 3;
				phaseTic = now;
				readyRun = 0;
			}
			else if (dt > 300)
				Fail(mo, "not ready after firing");
			break;
		case 3:
		{
			let h = RSR_Idle(mo);
			if (dt > 15 && readyRun >= 10 && h)
			{
				Console.Printf("V9T %s RELOADED t%d (%d tics) state %s |%s", guns[step], now, dt, StateName(mo), Inv(mo));
				phase = 0;
				step++;
			}
			else if (dt > CVInt('v9t_reload_tmo', 700))
				Fail(mo, "reload never finished");
			break;
		}
		}
	}

	// true when no real VR reload is running (or the pack has none: v8_stub.zs)
	static bool RSR_Idle(PlayerPawn mo)
	{
		return V9T_RSR.Idle(mo);
	}

	void Fail(PlayerPawn mo, String why)
	{
		Console.Printf("V9T %s FAIL t%d %s state %s |%s", guns[step], Level.maptime, why, StateName(mo), Inv(mo));
		phase = 0;
		step++;
	}

	void Reload(PlayerPawn mo, Weapon w)
	{
		String rn = "Reloading";
		class<Inventory> rc = rn;
		if (rc)
		{
			// BD22's src/Inputs.acs on +reload
			mo.GiveInventory(rc, 1);
			String a = "BDWeaponAction", b = "GoSpecial";
			class<Inventory> ac = a, bc = b;
			if (ac) mo.GiveInventory(ac, 1);
			if (bc) mo.GiveInventory(bc, 1);
			Console.Printf("V9T %s reload (BD22 tokens) t%d", guns[step], Level.maptime);
		}
		else if (mo.player.WeaponState & WF_WEAPONRELOADOK)
		{
			let rs = w.FindState("Reload");
			if (rs)
				mo.player.SetPsprite(PSP_WEAPON, rs);
			Console.Printf("V9T %s reload (engine Reload state) t%d", guns[step], Level.maptime);
		}
		else
			Console.Printf("V9T %s reload: not allowed now t%d", guns[step], Level.maptime);
	}
}

// handtone.zs (BD 2.0, owner 2026-10-27 20:05): "Hand Skin Tone", 18 steps over the FBX hands.
//
// THE TONES are pre-tinted copies of models/rsq/fbx/fbx_hand.png, made by tools/handtones.py (Lab
// recolour against the texture's own mean, so the shading survives; never hand-painted):
// models/rsq/fbx/tones/fbx_hand_tNN.png. Step 0 is the texture as drawn.
//
// HOW THEY ARE WORN, measured on the 17.3 rig before building this: A_ChangeModel's skin arguments
// (skinindex 0, skinpath, skin) on RSQ_GunSide DO re-skin the HUD hand (RenderHUDModel reads the
// psprite caller's modelData). So no MODELDEF block is copied. But that override is per ACTOR and per
// model index, not per frame, and the same actors also draw Ermac's hands (hand.png, ammo_hand.md3,
// m203_support.md3), whose UVs do not fit fbx_hand.png. So the override is switched on for a hand actor
// only while EVERY hand layer it is drawing is an FBX frame, and off otherwise:
//   which frames are FBX is read at startup from the MODELDEF lumps themselves (every RSQ_GunSide /
//   RSQ_Hands block whose Skin 0 is fbx_hand.png, its FrameIndex sprite+frame). Nothing is copied
//   and nothing has to be regenerated when other lanes edit hand rows: the rows are read as loaded.
//   A frame pairing an FBX gun hand with an Ermac support hand (the MiniGun's handle grip) shows
//   both as drawn rather than paint one with the other's texture.
//
// NOT TONED: the dual-wield and Purist weapon classes, whose MODELDEFs draw hands and gun under one
// actor (a per-actor skin override there would reach the gun), and Ermac's hands and the fists.
//
// rsq_hand_tone is a user cvar (your own hands); the hands are off in multiplayer (hands.zs).

class RSQ_HandTone : EventHandler
{
	const TONES = 18;		// 0 as drawn, 1..17 (tools/handtones.py TONES)

	Array<int> fbxSprite;	// SpriteID of each FBX hand frame, parallel to fbxFrame
	Array<int> fbxFrame;
	bool parsed;

	// what each hand actor is wearing now: -1 nothing (MODELDEF's own), else the tone
	Array<Actor> worn;
	Array<int> wornTone;

	override void OnRegister()
	{
		SetOrder(1001);	// after hands.zs has set this tic's frames
	}

	// ---------------------------------------------------------------- the FBX frames, from MODELDEF
	void Parse()
	{
		parsed = true;
		int lump = -1;
		while ((lump = Wads.FindLump("MODELDEF", lump + 1, Wads.AnyNamespace)) != -1)
			ParseLump(Wads.ReadLump(lump));
	}

	static String StripComments(String s)
	{
		String o = "";
		int i = 0, n = s.Length();
		while (i < n)
		{
			int c = s.ByteAt(i);
			if (c == 0x2F && i + 1 < n && s.ByteAt(i + 1) == 0x2F)
			{
				while (i < n && s.ByteAt(i) != 0x0A)
					i++;
				continue;
			}
			if (c == 0x2F && i + 1 < n && s.ByteAt(i + 1) == 0x2A)
			{
				int e = s.IndexOf("*/", i + 2);
				i = e < 0 ? n : e + 2;
				continue;
			}
			o.AppendCharacter(c);
			i++;
		}
		return o;
	}

	void ParseLump(String raw)
	{
		String t = StripComments(raw);
		t.ToLower();
		t.Replace("\t", " ");
		t.Replace("\r", " ");
		t.Replace("\n", " ");
		int at = 0;
		while (true)
		{
			int m = t.IndexOf("model ", at);
			if (m < 0)
				break;
			int ob = t.IndexOf("{", m);
			if (ob < 0)
				break;
			int cb = t.IndexOf("}", ob);
			if (cb < 0)
				break;
			at = cb + 1;
			// "model <class> {": the word between must be one of our two hand actors
			String head = t.Mid(m + 6, ob - m - 6);
			head.Replace(" ", "");
			if (head != "rsq_gunside" && head != "rsq_hands")
				continue;
			String body = t.Mid(ob + 1, cb - ob - 1);
			if (body.IndexOf("skin 0 \"fbx_hand.png\"") < 0)
				continue;
			Array<String> w;
			body.Split(w, " ", TOK_SKIPEMPTY);
			for (int i = 0; i + 3 < w.Size(); i++)
			{
				if (w[i] != "frameindex" || w[i + 3] != "0")
					continue;	// only frames of model 0, the hand mesh
				String sp = w[i + 1];
				sp.ToUpper();
				String fr = w[i + 2];
				fr.ToUpper();
				int sid = Actor.GetSpriteIndex(sp);
				if (sid < 0 || fr.Length() != 1)
					continue;
				fbxSprite.Push(sid);
				fbxFrame.Push(fr.ByteAt(0) - 0x41);
			}
		}
	}

	bool IsFbx(PSprite p)
	{
		int sid = int(p.Sprite);
		for (int i = 0; i < fbxSprite.Size(); i++)
			if (fbxSprite[i] == sid && fbxFrame[i] == p.Frame)
				return true;
		return false;
	}

	// ---------------------------------------------------------------- per tic
	override void WorldTick()
	{
		if (multiplayer)
			return;
		let pl = players[consoleplayer];
		if (!pl.mo)
			return;
		let cv = CVar.GetCVar('rsq_hand_tone', pl);
		int tone = cv ? clamp(cv.GetInt(), 0, TONES - 1) : 0;
		if (!parsed)
			Parse();

		// every hand actor drawing this tic, and whether all its drawn layers are FBX frames
		Array<Actor> who;
		Array<int> allFbx;
		for (let p = pl.psprites; p; p = p.Next)
		{
			let c = p.Caller;
			if (!c || !p.CurState)
				continue;
			Name cn = c.GetClassName();
			if (cn != 'RSQ_GunSide' && cn != 'RSQ_Hands')
				continue;
			if (p.Sprite == Actor.GetSpriteIndex('TNT1') || p.alpha <= 0)
				continue;
			int k = who.Find(c);
			bool f = IsFbx(p);
			if (k == who.Size())
			{
				who.Push(c);
				allFbx.Push(f ? 1 : 0);
			}
			else if (!f)
				allFbx[k] = 0;
		}
		for (int i = 0; i < who.Size(); i++)
			Wear(who[i], (tone > 0 && allFbx[i]) ? tone : -1);
	}

	// A_ChangeModel only when what an actor wears changes. skin 'None' / path "" = back to MODELDEF.
	void Wear(Actor a, int tone)
	{
		int k = worn.Find(a);
		if (k < worn.Size() && wornTone[k] == tone)
			return;
		if (tone > 0)
			a.A_ChangeModel('None', 0, "", 'None', 0, "models/rsq/fbx/tones/", Name(String.Format("fbx_hand_t%02d.png", tone)));
		else
			a.A_ChangeModel('None', 0, "", 'None', 0, "", 'None');
		if (k < worn.Size())
			wornTone[k] = tone;
		else
		{
			worn.Push(a);
			wornTone.Push(tone);
		}
	}
}

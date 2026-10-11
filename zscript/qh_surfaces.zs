// ============================================================================
// RS_QuestHands -- what textures are made of
//
// WHY THIS FILE EXISTS.
//
// RS_Ballistics picks its impact variant from the surface a round lands on --
// bullet.metal, bullet.wood, bullet.liquid. On our fork that answer comes from
// the ENGINE: SURFACES.txt is parsed in C++ and TexMan.GetSurface(tex) returns
// the name. Stock QZD 17.3 has no such native, so without this the whole
// impact system falls back to one generic puff and the port is pointless.
//
// So the lookup is reimplemented here in script. The DATA is unchanged --
// SURFACES.txt is copied across pattern for pattern, so a surface added there
// works here with no code.
//
// Cost is one glob match per DISTINCT texture, cached by TextureID after that.
// A map has a few hundred textures and a firefight has thousands of impacts, so
// in practice it is a hash lookup.
//
// Format, from the original:
//     surface metal
//     {
//         walls = "METAL*", "SUPPORT*"
//         flats = "FLAT23"
//     }
// `*` matches any run, `?` one character. `walls` keys on wall textures,
// `flats` on flats, `any` on both. A later rule or a later lump wins, so a map
// pack can reclassify; `surface none` un-tags.
// ============================================================================

class QH_SurfRule
{
	String pat;
	String surface;		// String, not Name: it goes straight into the String
						// cache, and formatting a Name into a String is a
						// conversion worth not depending on.
	int kind;			// 0 = walls, 1 = flats, 2 = any
}

class QH_Surfaces
{
	Array<QH_SurfRule> rules;

	// Cache keyed by TEXTURE NAME, not TextureID, for two reasons that are both
	// hard limits of stock QZD 17.3 rather than preference:
	//   1. TextureID exposes only IsValid/IsNull/Exists to script -- no int cast
	//      and no index, so it cannot be a key at all.
	//   2. Only Map<int,String> and Map<String,String> exist (maps.cpp declares
	//      FMap_I32_Str and FMap_Str_Str and nothing else). Map<int,int> and
	//      Map<Name,int> do not compile.
	// "" is stored for a known miss so a texture nothing claims is not re-matched
	// against every rule on every single impact.
	Map<String, String> cache;
	bool loaded;

	// ------------------------------------------------------------------------
	// Glob. `*` any run, `?` one character. Case-insensitive -- texture names
	// are, and the original table is written in upper case.
	// ------------------------------------------------------------------------
	static bool Glob(String pat, String str)
	{
		pat = pat.MakeUpper();
		str = str.MakeUpper();

		int p = 0, s = 0;
		int star = -1, mark = 0;
		int pl = pat.Length(), sl = str.Length();

		while (s < sl)
		{
			if (p < pl && (pat.ByteAt(p) == 63 || pat.ByteAt(p) == str.ByteAt(s)))	// 63 = '?'
			{
				p++; s++;
			}
			else if (p < pl && pat.ByteAt(p) == 42)								// 42 = '*'
			{
				star = p; p++; mark = s;
			}
			else if (star >= 0)
			{
				p = star + 1; mark++; s = mark;
			}
			else
			{
				return false;
			}
		}

		while (p < pl && pat.ByteAt(p) == 42) p++;
		return p == pl;
	}

	// ------------------------------------------------------------------------
	// Read every SURFACES lump in load order. Later wins, which is why rules are
	// appended and matched in reverse.
	// ------------------------------------------------------------------------
	void Load()
	{
		if (loaded) return;
		loaded = true;

		int lump = -1;
		while (true)
		{
			lump = Wads.FindLump("SURFACES", lump + 1, Wads.GlobalNamespace);
			if (lump < 0) break;
			ParseOne(Wads.ReadLump(lump));
		}
	}

	private void ParseOne(String text)
	{
		Array<String> lines;
		text.Split(lines, "\n");

		String cur = "";

		for (int i = 0; i < lines.Size(); i++)
		{
			String ln = lines[i];

			// strip // and # comments
			int c = ln.IndexOf("//");
			if (c >= 0) ln = ln.Left(c);
			c = ln.IndexOf("#");
			if (c >= 0) ln = ln.Left(c);

			// NOT Filter() -- that interprets backslash escapes, it does not
			// trim, and it would mangle a pattern.
			ln = Trim(ln);
			if (ln.Length() == 0) continue;

			if (ln.Left(8).MakeLower() == "surface ")
			{
				cur = Trim(ln.Mid(8));
				continue;
			}
			if (ln == "{" || ln == "}") continue;

			int eq = ln.IndexOf("=");
			if (eq < 0) continue;

			String key = Trim(ln.Left(eq)).MakeLower();
			int kind = (key == "walls") ? 0 : (key == "flats") ? 1 : (key == "any") ? 2 : -1;
			if (kind < 0) continue;

			// the values are quoted, comma separated
			String rest = ln.Mid(eq + 1);
			Array<String> parts;
			rest.Split(parts, ",");

			for (int k = 0; k < parts.Size(); k++)
			{
				String v = Trim(parts[k]);
				v.Replace("\"", "");
				v = Trim(v);
				if (v.Length() == 0) continue;

				let r = new("QH_SurfRule");
				r.pat = v;
				r.surface = cur;
				r.kind = kind;
				rules.Push(r);
			}
		}
	}

	static String Trim(String s)
	{
		int a = 0, b = s.Length();
		while (a < b)
		{
			int ch = s.ByteAt(a);
			if (ch != 32 && ch != 9 && ch != 13) break;
			a++;
		}
		while (b > a)
		{
			int ch = s.ByteAt(b - 1);
			if (ch != 32 && ch != 9 && ch != 13) break;
			b--;
		}
		return s.Mid(a, b - a);
	}

	// ------------------------------------------------------------------------
	// What is this texture made of? 'None' when nothing claims it.
	//
	// isFlat picks which rules apply, exactly as the engine keys on the
	// texture's own type.
	// ------------------------------------------------------------------------
	Name Of(TextureID tex, bool isFlat)
	{
		Load();
		if (!tex.IsValid()) return 'None';

		String tn = TexMan.GetName(tex);
		if (tn.Length() == 0) return 'None';

		String key = (isFlat ? "f:" : "w:") .. tn;

		if (cache.CheckKey(key))
		{
			String hit = cache.Get(key);
			return hit.Length() > 0 ? Name(hit) : 'None';
		}

		String found = "";

		// Later rules win, so walk backwards and take the first hit.
		for (int i = rules.Size() - 1; i >= 0; i--)
		{
			let r = rules[i];
			if (r.kind == 0 && isFlat) continue;
			if (r.kind == 1 && !isFlat) continue;
			if (Glob(r.pat, tn))
			{
				// `surface none` un-tags: it is a real rule meaning "nothing
				// claims this", and it must beat the earlier rule it overrides,
				// so it still breaks the loop -- it just leaves `found` empty.
				if (r.surface.MakeLower() != "none") found = r.surface;
				break;
			}
		}

		cache.Insert(key, found);
		return found.Length() > 0 ? Name(found) : 'None';
	}
}

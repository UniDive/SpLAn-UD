def UD_English_GENTLE(meta):
	return int(meta["meta::speakerCount"])>0


def UD_English_GUM(meta):
	return  meta["meta::genre"] in ["conversation", "interview", "speech"]


def UD_Greek_GDT(meta):
	return "ep-session" in meta["sent_id"]


def UD_Highland_Puebla_Nahuatl_ITML(meta):
	return ".eaf" in meta["sent_id"]


def UD_Scottish_Gaelic_ARCOSG(meta):
	return meta["sent_id"].startswith("c") or \
			meta["sent_id"].startswith("n") or \
			meta["sent_id"].startswith("p") or \
			meta["sent_id"].startswith("s")


def UD_Western_Sierra_Puebla_Nahuatl_ITML(meta):
	return "Frog_Story" in meta["sent_id"]
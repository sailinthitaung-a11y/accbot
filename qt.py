# ====== IMPORTS ======
from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins
import asyncio
import time
import re
from flask import Flask
from threading import Thread

# ====== API CONFIG ======
api_id = 21308016
api_hash = "9a483e059bcb0904e9f367418076091e"

# ====== MAIN OWNER ======\
MAIN_OWNER = [7781882070,6543902488,7690724545]

# ====== AUTO REPLIES ======
# (NOTE: Your original auto_replies list is long, so I've shortened it for display.
# It should remain fully intact in the final file.)
auto_replies = [
     "ဖာသည်မသားမင်းမေစောက်ဖုတ်လီးနဲ့ကလိလဲလီးတောင်ချင်စရာမကောင်းလိုက်တာကွာ😂✌️",
        "ခွေးမသားသတ္တိရှိရင်မင်းအမေဖာသည်မကိုအော်ဆဲပြလိုက်ပါလား😂✌️",
        "ငါလိုးမသားလီးလုပ်နေတာလားပျင်းစရာကောင်းလိုက်တာ😂✌️",
        "ကိုမေကိုလိုးစောက်နုပြန်ဆဲလေငြိမ်ခံမနေနဲ့😂✌️",
        "မအေလိုးမင်းမေစောက်ပက်လိမ်ဆွဲပစ်မယ်ကျေနပ်လား😂✌️",
        "မင်းရဲ့ချစ်ရပါသောဖခင်ကြီးဖြစ်ချင်ပါတယ်မင်းမေပေးလိုးပါ😂✌️",
        "မအေလိုးဝက်😂✌️",
        "ဖာသည်မသားသေချာကိုက်😂✌️",
        "ဒီလိုဆိုမင်းအမေဖာသည်မပဲ😂✌️",
        "မအေလိုးကိုက်ထားဖာသည်မသားကြောင်ကြည့်မနေနဲ့😂✌️",
        "ဘမောတဲ့ဘောမ ဝဠ်ကြွေးရွှိသမျှအောင့်အီးသာခံလိုက်😂✌️",
        "သာဓုနှစ်ကြိမ်ခေါ်လိုက်ဘောမ မင်းကိုနောက်တစ်ကြိမ်ပေးမခေါ်ဘူးမင်းဒီဘဝဒီမျှဝဠ်ကြွေးရှိသမျှကုန်အောင်သာဆပ်😂✌️",
        "မအေလိုးစောက်သခေါရပ်ကြည့်မနေနဲ့မင်းအမေငါတက်လိုးလိုက်မယ်😂✌️",
        "မအေလိုးဝက်ကိုက်မှာသာကိုက်စကားပလ္လင်ခံမနေနဲ့နောက်ဆုံးမင်းဒီဘူတာပဲဆိုက်မှာ😂✌️",
        "နှမလိုးဘောမကိုက်ဆိုကုန်းသာကိုက်နောက်အံကိုကြိတ်ထားရဲရဲသာကိုက်😂✌️",
        "ဥုံဘောမငါ့အမိန့်နဲ့မင်းအမေဖာသည်မဖြစ်စေ😂✌️",
        "မအေလိုးပေါက်စခေါင်းကိုငုံ့ထားမင်းကိုဆုံးမနေတာမင်းဆရာကံကြီးထိုက်မယ်😂✌️",
        "နှမလိုးဖက်တီးမင်းအဖေဝက်ကြီးအပြင်သွားတုန်းမင်းအမေကိုခိုးလိုးပြစ်မယ်😂✌️",
        "ပိုင်ရာဆိုင်ရာများငါ့အမိန့်နဲ့ဒီဖာသည်မသားအမေကိုချုပ်လိုးကြစမ်း😂✌️",
        "ဟိတ်ကောင်စောက်ဝက်စောက်ခွက်ကိုခြောက်ချက်တိတိရိုက်ခံရမယ်😂✌️",
        "မင်းအဖေမူးပြီးမင်းအမကိုတက်လိုးသွားဦးမယ်ကျပ်ကျပ်သတိထား😂✌️",
    "၁၆၆၇မှာ Newtonက ပန်းသီးကျွေကျလို့ ကမ္ဘာမြေကြီးဆွဲအားရှိတယ်လို့ပြောခဲ့တာမဟုတ်ဘူး မင်းအမေကိုလိုးရင်း အလိုးကြမ်းတော့ မင်းအဖေဖာသည်မက ပန်းသီးပင်နဲ့ခေါင်းတိုက်မိပြီး ပန်းသီးကျွေကျလာတာ အဲဒါကို နယူးတန်က ဖုံးကွယ်ချင်တော့ ကမ္ဘာမြေကြီး ဆွဲအားရှိကြောင်း သက်သေပြခဲ့တာလို့ပြောတာ😂✌️",
        "နယူးတန်ကပြောခဲ့တယ် မင်းအမေဖာသည်မတဲ့ အဲ့အချိန်မှာအိုင်းစတိုင်းကဖြေရှင်းချက်ပေးပီး မင်းအမေစောက်ဖုတ်မဲကြောင်းအတည်ပြုခဲ့တယ်၊ ကမ္ဘာကျော်သိပ္ပံပညာရှင်တွေစူးစမ်းရင်းမင်းအမေစောက်ပတ် black hole ထက်ကျယ်ကြောင်းအတည်ပြုခဲ့သည်😂✌️",
        "မသိဘူး ကိုမေကိုလိုးလိုက်တပည့်မသိချင်ဘူးကွာ ကိုမေကိုဂျွမ်းပစ်လိုးလိုက်😂✌️",
    "ဖာသည်မသားငါကလစ်ရင်မင်းစိတ်ထိခိုက်တယ်မလား ကလစ်တယ်ကွာဘာတတ်နိုင်သေးလဲ😂✌️",
    "ငါလိုးမ အာပေးတူ ဆဲတာပျော့လိုက်တာ ထိထိမိမိဆဲလေ🤞😏",
    "စောက်တောပိန်း🤞😳",
    "စောက်ချိုးအခမဲ့ပြင်ပေးတယ်🤞😁",
    "ကိုမေကိုလိုး ကြောက်ရင်ကြောက်တယ် လို့အခုကတည်းကပြော လျှော်ပေးမယ်🤞🥶",
    "ကောင်းပြီ မင်းအမေဖာသည်မဖြစ်ပြီ🤞😂",
    "တောင်းပန်ပါတယ်ကွာ မင်းအမေကိုလိုးမိတဲ့အတွက်🤞🥶",
    "ဒီပုံစံအတိုင်းဆိုမင်းအမေဖာသည်မပဲဖြစ်ရမယ် 😂😂😂",
    "ငါ့ကိုအာခံရင်မင်းအမေဖာသည်မဖြစ်စေ👉😂",
    "မင်းလောင်နေတာလား👉😂 🤔",
    "မင်းအမေကြက်မဆို👉😂 😂",
    "ဟာတကယ်လား မင်းအမေဖာသည်မကြီးဆိုတာ👉😂 😁",
    "ငါ့ကို ကြောက်ပါပြီလို့ ၃ကြိမ်ပြော လွတ်ပေးမယ်👉😂 😉",
    "မင်းအမေသွားပြောလေ👉😂 😂",
    "မင်းအားကိုးတဲ့ကောင်တွေ ငါ့ရှေ့ရောက်ရင် ဒူးထောက်လက်မြောက်ရတယ်👉😂 😁",
    "မင်းအမေသွားပြောလေ👉😂 😂",
    "မင်းဆရာငါ ကလစ်ရင်မင်းစိတ်ထိခိုက်တယ်မလား ကလစ်တယ်ကွာဘာတတ်နိုင်သေးလဲ👉😂",
    "ရုပ်ဆိုးတဲ့ကောင်လေး👉😂 😂",
    "ဟျောင့်ခွေး👉😂",
    "ဟမင်းအဖေခွေးကြီးသေပြီပေါ့👉😂",
    "ငါးပါးမှောက်နေပြီလား👉😂",
    "ဖအေမြင်ရင်မင်းဘဲရုန်းကန်နေတာပါ👉😂",
    "မင်းအစွယ်တုံးရီးနဲ့ ကိုက်လေ👉😂",
    "မင်းအမေဖာသည် ဖြစ်တာမြင်ချင် ငါ့ကိုဆဲလေ🤞😁",
    "အုံဖွမင်းအမေဖာသည်မ🫵😂",
    "မင်းအမေလင်ကငါလေ👉😂",
    "ကိုမေကိုလိုးလေး သတိထား🫵😂",
    "ကောင်းပြီ မင်းအမေဖာသည်မကြီးပေါ့👉😂",
    "နဂိုကတည်းကပျင်းနေတာ ကျေးဇူးပဲ အဆဲခံပေးလို🤞🤨",
    "ငါလိုးမသား အိမ်ကအမေ ဆဲခိုင်းတောင်း မင်းထက် ကောင်းအုန်းမယ်🫵😂",
    "ကောင်းပြီ မင်းအမေကိုလိုးတာ ငါပဲ👉😂",
    "မင်းအဖေခွေးကြီးသွားပြောပါလား👉😂",
    "ကိုမေကိုလိုး ဘယ်ထိခံမလည်း ငါ ကတော့မသေမချင်း👉😂",
    "ဟ မင်းအမေကိုလိုးတာငါပေါ့🤞😜",
    "ငါဆရာကံကြမ္မာငင် သွားမယ်မှတ်👉😂",
    "မင်းအမေကိုလိုးတာငါပဲ🤞😂",
    "တောင်းပန်ပါတယ်ကွာ မင်းအမေကိုလိုးမိတဲ့အတွက်🤞🥶",
    "ဒေါသတွေထွက်ပြီးငယ်ထိပ်ကြီနီလာပါလားဘယ်လိုလည်းဘောမ စိတ်အတော်ညစ်ပြီးအပေါသွေးအောက်သွေးမမျှတောဘူးလား😂👈😏",
    "မင်းအမေဖာသည်မလားကောင်းပြီ😂🫵",
        "မသိချင်ဘူးဆက်တိုက်ကိုက်😂✌️",
        "အတာမင်းမေစပဖြစ်တာလား😂👈",
        "ဆဲရင်ခံခိုင်းရင်လုပ်😂✌️",
        "ဖက်ဆစ်နိုင်တယ်အဲ့တော့လီးဖြစ်သလား😂👌",
        "တပည့်သေမယ်😂🫵",
        "ဟျောင့်ခွေး အစွယ်ကောင်းနေတာလား😂✌️",
        "မင်းအမေဖာသည်မဆိုတာတစ်ကယ်လား😂👈",
        "ဖာသည်မသား😂👌",
        "မင်းအမေပိပိ😂🫵",
        "မအေလိုးစောက်ရူး လည်တော့လည်တယ်မင်းတစ်ပတ်မပြည့်ဘူး😂✌️",
        "မင်းအမေကိုဖက်ဆစ်ကဆရာတွေဝိုင်းလိုးမိလား😂👌",
        "ငါလိုးမစောက်ရူးကူကယ်ရာမဲ့ပြနေတာလားမင်းစကားဝိုင်းရဲ့အလယ်မှာသိမ်ငယ်နေရပြိလား😂👈",
        "မအေလိုးဘောမ မင်းဘောမတောထဲကမထွက်ဘူးလားစောက်ခွေး😂🫵",
        "စောက်တောသားမင်းမေဖာသည်မဆက်ဖြစ်နေမှာ ဧကန်မုချဘဲ😂✌️",
        "မင်းအဖေဆိုတဲ့ကောင်ပါပေးတယ်သားပေါက်",
        "စောက်ငနုလိုကောင် နိုင်အောင်ကိုက်လေ",
        "မင်းအမေလိုအထန်မကိုပိုင်ဆိုင်ရတဲ့မင်းအတွက်ဂုဏ်ယူတယ်",
        "ဖာသည်မသားမင်းဘယ်လိုနိုင်မှာလဲမင်းယှဉ်ဆဲနေတာသခင်သန်းဝေယံနိုင်လေ",
        "ငါ့အမိန့်မရပဲဘာကိုနားချင်တာလဲခွေးမသားမျိုး",
        "ဟျောင်နှမလိုးကျပ်မပြည့် ငါ့ဖွားတော်နဲ့ကော နပန်းလုံးမလား",
        "ဟေ့ရောင်ဖာသည်မသားငါလီးကြီးကိုမင်းအမေအဖုတ်ထဲစိမ်လိုက်ရမလား",
        "ကလစ်လေကလေဘာလို့နားနေတာလဲလက်ညောင်းသွားလို့လား",
        "ခွေးမသားလေးကလဲမင်းစောက်သုံးကျတာဘာရှိလဲငါတို့တော့မင်းအမေဖီးလ်လာအောင်ကောင်းလိုးတတ်တာနဲ့တင်မင်းထက်သာနေပြီ",
        "စောက်ရူးမသားလေး‌လာကိုက်လေဘာလိုဂျောင်ထဲမာမာန်ဖီနေရတာလဲ",
        "ဟေ့ရောင်ဖာသည်မသားလေး မောနေပြီလား ပေးမနားနိုင်ဘူးကိုက်ထား",
        "ဖာသည်မသားလေးကိုက်စရာရှိကိုက်ပါဟ ဘယ်ငေးနေတာလည်း",
        "မင်းအမေစဖုတ်ဘာလို့မဲတာလည်း အဖြေရှာမရဖြစ်နေတာလား",
        "မင်းအမေကိုစောက်ဖုတ်အမဲရောင်ကနေအနီရောင်ပြောင်းသွားအောင်တီးထုတ်ပေးလိုက်ရမလား",
        "မအေလိုးဘောမ သန်းဝေယံနိုင်ဆိုတာနဲ့တင်မင်းကြောက်နေတာလား",
        "မင်းလိုစောက်သုံးမကျတဲ့ကောင်ဖက်ဆစ်ထဲမှာရှိရင်ကျွန်လိုခိုင်းစားပစ်လိုက်ပြီ",
        "မအေလိုးဘာဖြစ်တာလဲငါကအထှာကျ‌လွန်းတော့မင်းငါ့ပုံစံကော်ပီဖို့အကြံထုတ်နေတာလား",
        "ခွေးမသားလေးကိုက်ထားလေးဘာအားလျှော့ချင်တာလဲနိုင်ချင်ရင်ကိုက်ဒါမယ့်မင်းမနိုင်ဘူး",
        "အေ့တပည့်ရဲ့မင်းဆရာကငါပဲဘာဖြစ်လို့လဲခွေးမသားကိုက်ထားလေ",
        "မင်းစာရိုက်နေတာလား ငါဖုန်းထဲမှာခွေးလေး‌ရေးထားသလို့ပဲဟ",
        "ဖာသည်မသားညံ့ချက်ပါလားလူကနုံချာချာနဲ့အပျင်းမပြေလိုက်တာကွာ",
        "မအေလိုးရေဝေးဝေးကဟောင်မင်းဆီကဘောဆော်နံတယ်",
        "မင်းအမေကြီးလမ်းမှာခွေးတစ်ကောင်နဲ့မိတ်လိုက်နေတာငါတွေ့လိုက်တယ်",
        "ဟေ့ရောင်ဈေးမရတဲ့ဖာသည်မသားကိုက်လေဘယ်ငေးတာလဲ",
        "မင်းအမေဖာသည်မဆိုတာမင်းမပြောလဲငါသိပါတယ်",
        "ဖက်ဆစ်ကိုနိုင်ချင်ရင်ဆုတောင်းလေငနဲရပူဖောင်းကြီးကြီးရလိမ့်မယ်",
        "မအေလိုးလေးငါ့အထှာခိုးဖို့မကျန်နဲ့မင်းနဲ့မလိုက်ဖက်ဘူး",
        "ခွေးမသားမင်းအမေကိုလေချွန်ပြီးလိုးလိုက်ရမလား",
        "ဟေမအေလိုးဘောမကိုက်လေကွဘာကြောင်ကြည့်နေတာလဲ",
        "စက္ကန့်နဲ့အမျှထွက်လာတဲ့ငါ့နဲ့flowတွေကြောင့်မင်းကြောက်စိတ်ဝင်နေပလား",
        "မအေလိုးမင်းအမေဖာသည်မဆိုတာဝန်ခံပီလား",
        "မင်းမှာလွတ်လမ်းမရှိတော့ဘူးလာရာလမ်းအတိုင်းတည့်တည့်သွားရင်မင်းအမေနဲ့ငါနဲ့ လိုးနေတာမြင်ရလိမ့်မယ်",
        "စောက်ဝက်ကြီးဗြောင်လိမ်ဗြောင်စားလုပ်မယ်မကြံနဲ့မင်းအမေဖာသည်မ မဟုတ်လား",
        "ဟေ့ရောင်မင်းအမေလိုးတဲ့အခါဘယ်လိုအော်လဲသိချင်ရင်မင်းစောက်ခွက်ကိုရှေ့ကပ်ထား",
        "မင်းအမေကိုဦးနှောက်ပါပေါက်ထွက်သွားအောင်းပါးစပ်ပေါက်ထဲလီးထို့ထည့်မယ်",
        "ဖာသည်မသားဖက်ဆစ်နိုင်ပြီလေဘာငြင်းချင်သေးတာလဲ",
        "ဖက်ဆစ်ကိုနိုင်ချင်ရင်ငါ့ကိုအရင်ကျော်မှရမယ်ဒါမယ့်ဘယ်လိုမှမဖြစ်နိုင်ဘူးဆိုတာမင်းသိ",
        "ငါ့ကိုယ်ထဲမှာရှိနေတဲ့ဖက်ဆစ်သွေးတွေနဲ့ဖာသည်မသွေးနဲ့အရောမခံနိုင်လို့မင်းအမေကိုမလိုးပဲလွှတ်ပေးလိုက်ပါပြီ",
    "မင်းအမေမင်းမလိုးရင်မင်းအမေငါပဲလိုးတော့မယ်",
    "မင်းမေ‌ေစာက်ပက်လားစောက်ဖာသည်မသား",
    "ကိုမေကိုဘေးတစ်စောင်းလိုးမသား",
    "မင်းမေမင်းလိုးတာလား",
    "ကိုက်တာလားအဲ့တာ",
    "ဖာသည်မသားလီးဖြစ်တာလား",
    "မသိပါဘူးဘောမရာကိုက်လေ",
    "ခ ခလေးငယ်ချစ်စဖွယ် မင်းအမေကိုအပျော်ကြံ",
    "မင်းအမေသေလိုလားအဲ့တာ",
    "မင်းမေလိုးဖြစ်တာလားခွေးမသား",
    "မင်းအမေကိုချစ်တယ်ပြီးရင်လိုးမယ်",
    "လီးစောင်းနဲ့ခုတ်ချလိုက်လိုခွေးမသား",
    "မင်းအဖေဆိုတဲ့ကောင်ပါပေးတယ်သားပေါက်",
    "စောက်ငနုလိုကောင် နိုင်အောင်ကိုက်လေ",
    "မင်းအမေလိုအထန်မကိုပိုင်ဆိုင်ရတဲ့မင်းအတွက်ဂုဏ်ယူတယ်",
    "ဖာသည်မသားမင်းဘယ်လိုနိုင်မှာလဲမင်းယှဉ်ဆဲနေတာဖက်ဆစ်Fdrလေ",
    "ငါ့အမိန့်မရပဲဘာကိုနားချင်တာလဲခွေးမသားမျိုး",
    "ဟျောင်နှမလိုးကျပ်မပြည့် ငါ့ဖွားတော်နဲ့ကော နပန်းလုံးမလား",
    "ဟေ့ရောင်ဖာသည်မသားငါလီးကြီးကိုမင်းအမေအဖုတ်ထဲစိမ်လိုက်ရမလား",
    "ကလစ်လေကလေဘာလို့နားနေတာလဲလက်ညောင်းသွားလို့လား",
    "ခွေးမသားလေးကလဲမင်းစောက်သုံးကျတာဘာရှိလဲငါတို့တော့မင်းအမေဖီးလ်လာအောင်ကောင်းလိုးတတ်တာနဲ့တင်မင်းထက်သာနေပြီ",
    "စောက်ရူးမသားလေး‌လာကိုက်လေဘာလိုဂျောင်ထဲမာမာန်ဖီနေရတာလဲ",
    "ဟေ့ရောင်ဖာသည်မသားလေး မောနေပြီလား ပေးမနားနိုင်ဘူးကိုက်ထား",
    "ဖာသည်မသားလေးကိုက်စရာရှိကိုက်ပါဟ ဘယ်ငေးနေတာလည်း",
    "မင်းအမေစဖုတ်ဘာလို့မဲတာလည်း အဖြေရှာမရဖြစ်နေတာလား",
    "မင်းအမေကိုစောက်ဖုတ်အမဲရောင်ကနေအနီရောင်ပြောင်းသွားအောင်တီးထုတ်ပေးလိုက်ရမလား",
    "မအေလိုးဘောမ ဖက်ဆစ်‌‌Fdrဆိုတာနဲ့တင်မင်းကြောက်နေတာလား",
    "မင်းလိုစောက်သုံးမကျတဲ့ကောင်ဖက်ဆစ်ထဲမှာရှိရင်ကျွန်လိုခိုင်းစားပစ်လိုက်ပြီ",
    "မအေလိုးဘာဖြစ်တာလဲငါကအထှာကျ‌လွန်းတော့မင်းငါ့ပုံစံကော်ပီဖို့အကြံထုတ်နေတာလား",
    "ခွေးမသားလေးကိုက်ထားလေးဘာအားလျှော့ချင်တာလဲနိုင်ချင်ရင်ကိုက်ဒါမယ့်မင်းမနိုင်ဘူး",
    "အေ့တပည့်ရဲ့မင်းဆရာကငါပဲဘာဖြစ်လို့လဲခွေးမသားကိုက်ထားလေ",
    "မင်းစာရိုက်နေတာလား ငါဖုန်းထဲမှာခွေးလေး‌ရေးထားသလို့ပဲဟ",
    "ဖာသည်မသားညံ့ချက်ပါလားလူကနုံချာချာနဲ့အပျင်းမပြေလိုက်တာကွာ",
    "မအေလိုးရေဝေးဝေးကဟောင်မင်းဆီကဘောဆော်နံတယ်",
    "မင်းအမေကြီးလမ်းမှာခွေးတစ်ကောင်နဲ့မိတ်လိုက်နေတာငါတွေ့လိုက်တယ်",
    "ဟေ့ရောင်ဈေးမရတဲ့ဖာသည်မသားကိုက်လေဘယ်ငေးတာလဲ",
    "မင်းအမေဖာသည်မဆိုတာမင်းမပြောလဲငါသိပါတယ်",
    "ဖက်ဆစ်ကိုနိုင်ချင်ရင်ဆုတောင်းလေငနဲရပူဖောင်းကြီးကြီးရလိမ့်မယ်",
    "မအေလိုးလေးငါ့အထှာခိုးဖို့မကျန်နဲ့မင်းနဲ့မလိုက်ဖက်ဘူး",
    "ခွေးမသားမင်းအမေကိုလေချွန်ပြီးလိုးလိုက်ရမလား",
    "ဟေမအေလိုးဘောမကိုက်လေကွဘာကြောင်ကြည့်နေတာလဲ",
    "စက္ကန့်နဲ့အမျှထွက်လာတဲ့ငါ့ရဲ့flowတွေကြောင့်မင်းကြောက်စိတ်ဝင်နေပလား",
    "မအေလိုးမင်းအမေဖာသည်မဆိုတာဝန်ခံပီလား",
    "မင်းမှာလွတ်လမ်းမရှိတော့ဘူးလာရာလမ်းအတိုင်းတည့်တည့်သွားရင်မင်းအမေနဲ့ငါနဲ့ လိုးနေတာမြင်ရလိမ့်မယ်",
    "စောက်ဝက်ကြီးဗြောင်လိမ်ဗြောင်စားလုပ်မယ်မကြံနဲ့မင်းအမေဖာသည်မ မဟုတ်လား",
    "ဟေ့ရောင်မင်းအမေလိုးတဲ့အခါဘယ်လိုအော်လဲသိချင်ရင်မင်းစောက်ခွက်ကိုရှေ့ကပ်ထား",
    "မင်းအမေကိုဦးနှောက်ပါပေါက်ထွက်သွားအောင်းပါးစပ်ပေါက်ထဲလီးထို့ထည့်မယ်",
    "ဖာသည်မသားဖက်ဆစ်နိုင်ပြီလေဘာငြင်းချင်သေးတာလဲ",
    "ဖက်ဆစ်ကိုနိုင်ချင်ရင်ငါ့ကိုအရင်ကျော်မှရမယ်ဒါမယ့်ဘယ်လိုမှမဖြစ်နိုင်ဘူးဆိုတာမင်းသိ",
    "ငါ့ကိုယ်ထဲမှာရှိနေတဲ့ဖက်ဆစ်သွေးတွေနဲ့ဖာသည်မသွေးနဲ့အရောမခံနိုင်လို့မင်းအမေကိုမလိုးပဲလွှတ်ပေးလိုက်ပါပြီ",
    "ဟေ့ရောင်သေးသေးလေးမင်းမိဘတွေဆုံးပီလား",
    "မင်းအိပ်နေတဲ့အချိန်မင်းအမေငါလိုးလိုက်မိပြီ",
    "ကိုက်အားကောင်းတယ်မင်းအမေဖာသည်မ",
    "မအေလိုးပေါက်စနကိုက်ထား",
    "မအေလိုးမြှောက်ပေးရင်ဂွေးတက်အောင်မင်းအမေလိုးတာလား",
    "ရောယောင်နေတဲ့ ပေါကြောင်မ",
"ငါဘောထောင်ပြရင်စုတ်မလား",
"ငနုက အောက်လုံးကရုန်းမထွက်နိုင်",
"ဘာတွေလျှောက်ရေးနေတာ စောက်ရူးအကွပ်နက်",
"မသက်တိုင်တာတွေလျှောက်ပြောပီး ကြမ်းတယ်ထင်ရင် ဖင်လှန်ထား",
"ပန်းခြံမှာ နန်းစံအောင်လို့ကိုယ်ဖင်ကိုယ်လှန်ထောင်းနေ",
"ဂလေဂချေကွာ ဖုန်းလေးတစ်လုံးရဟိုရေးဒီရေးရှောက်ရေးဟိုလုပ်ဒီလုပ်ရှောက်လုပ် ဖင်ကိုအသေမုန်းကြုံးပေးလိုက်ရ",
"တိကျသေချာတဲ့ကြောင်းအရာကိုမပြောပဲ လျှောက်ဆဲနေတာစာမတတ်ရင် translate သုံးလေ",
"အဲ့တာ ဦးနှောင်မရှိလို့ လိုက်ပြောနေလည်း မောတာပဲရှိနယ်",
"သွေးရူးသွေးတန်းပတ်ဟောင်နေတယ်",
"စကားတောင် ဖြစ်မြောက်အောင်မပြောနိုင်အဲ့တာနဲ့များ ဘယ်နားလူရာဝင်ချင်",
"ဖြတ်ကန်လိုက်မယ်မအေလိုးဝမရှိပဲဝိမလုပ်နဲ့",
"ယျောင်စက်ဘီးစောက်စုတ်စီးတဲ့ခွေးရေးလေ",
"ရေတိမ်ရင်ကူးရခက်သလို အတွေးတိမ်ရင်တောသားမှန်းသိတယ်",
"ငိုးမစောက်ကုလား မင်းဘုတ်နေတာလူမိပီ",
"ထိရောက်မှုလဲမရှိဖြစ်ထွန်းမှုလဲမရှိ ညဏ်ရည်လဲမမှီ",
"လီးနက်ပိတ်ရိုက်လိုက်လို့မအေဖင်ထဲပြန်ဝင်ချင်တာလား",
"အလျင်မလိုနဲ့ ဖြေးဖြေးကိုက်",
"သွားကြွတ်အောင်",
"မင်းဆရာကိုယ်တိုင်ဆင်းရိုက်ပေးမယ်",
"မင်းအမေကို အောက်ထပ်ကငရဲမင်းက မီးပူသံလျပ်နဲ့ တက်ထိုးတာ မင်းအမေသေနေပြီ",
"မင်းစောက်သုံးမကျလို့",
"မင်းအမေဝက်ကုလားတက်လိုးခံရပြီ စောက်သုံးမကျတဲ့ခွေး",
"ဖာခံမှ စားရတဲ့ငွေနဲ့",
"မင်းရိုက်နေတဲ့စာနဲ့",
"မအက်စပ်ဘူး ချီးပဲစားနေ",
"စောက်ခွက်ကိုကပ်တရာလမ်းမနဲမိတ်ဆက်ပေးရမှလား",
    "ကိုမေကိုလိုးစောက်တောသား ၂၀၂၅ရောက်တာတောင်မင်းလိုကောင်ခေတ်နောက်ကျတုန်းလား",
    "မင်းလိုကောင်ဆဲရတာ ရပ်ကွက်ထဲကလေးတစ်ယောက်စီကပါးရိုက်ပြီးမုန့်လုရတာထက်တောင်လွယ်နေသေးတယ်",
    "ဟိတ်မင်းအမေသေပြီဖာသယ်မသား",
    "လီးနက်ပိတ်ရိုက်လိုက်လို့မအေဖင်ထဲပြန်ဝင်ချင်တာလား",
    "မအူအလည်ဖြစ်နေတာလား ကိုမေကိုလိုးစောက်ခြောက်",
    "ငါလိုးမသားစောက်ခွက်က တစ်ရေးနိုးလို့ထကြည့်ရင်တောင် ၅ပြား မတန်ဘူး",
    "skykingဆိုတာကြယ်တွေရဲ့အရှင်ပဲမင်းတို့မှတ်ထား",
    "ဟုမ်းမိတ်ဆိုပြီး မင်းအမေကိုအမုန်းကြိတ်ပေးရမှလား",
    "မအေလိုးကြက်ပေါက်စ ပိကျိပိကျိနဲ့မင်းဘာတွေအော်နေတာလဲ",
    "မင်းစာဘယ်သူဖတ်လို့မင်းကဘာတွေလုရိုက်ချင်နေတာလဲ",
    "ကိုမေကိုလိုးကတော့လီးတွေဝင်ဝင်ပြောနေတာလား",
    "ဖာသည်မသားလီးဖြစ်လို့အော်နေတာလား",
    "ခွန်းတုန့်မပြန်နဲ့ မင်းအဖေလိုတော့ခွင့်လွှတ်မှာမဟုတ်ဘူးဖာသည်မသား",
    "မင်းလိုကောင်ငါ့တပည့်နဲ့ဆဲခိုင်းရင်တောင်မတန်ရာကျအုန်းမယ်",
    "ဟုမ်းမိတ်ဆိုပြီး မင်းအမေကိုအမုန်းကြိတ်ပေးရမှလား",
    "ကိုမေကိုလိုးကတော့လီးတွေဝင်ဝင်ပြောနေတာလား",
    "မပြောချင်လို့ကြည့်နေတာအကောင်းမှတ်မနေနဲ ငါလိုးမခိုင်းခွေး",
    "မင်းကိုနိုင်ဖို့ ငါ့ရဲ့ အင်အား 1% တောင်သုံးစရာမလိုဘူး",
    "ဆဲရင်သေချာဆဲလေ မင်းစောက်ခြောက်လား နာနာဆဲပါဟ",
    "ကို့စောက်ခွက် ကိုမှန်ထဲ ပြန်ကြိ ယောကျ်ား ကောဟူတ်ရဲ့ လားဆိုတာ လီးပါမှ ယောကျ်ား မဟူတ်ဘူး",
    "telegram အင်ပါယာမင်းသားကိုသိလား",
    "ဟျောင့်တောဝက်ကြီးဖြည်းကိုက်",
    "မအေလိုးဝက်ကုလားမင်းသေမယ်",
    "ဟိတ်ကောင် ခွေးမသားပိစိသေးသေးလေးပြေးထားကွ",
    "မင်းအမေဖာသယ်မကြီးမနေ့ကဆုံးလိုဆို",
    "သခင်PKလက်မြန်တာမင်းသိပြီလား",
    "သခင်မလာတုန်းကလိုက်ကိုက်နေပြီးသခင်လာမှပြေးတာဘာအထာလဲကွ",
    "ဟိတ်ကောင်ငနွားရုန်းထားစမ်း",
    "မင်းဆရာPkကွဘာမှတ်နေလဲ",
    "အေးPkတပဲ့လေးကိုမေကိုလိုးပလိုက်",
    "ဘာတွေရှောက်ကြည့်နေတာဝင်ကိုက်ဘောမ",
    "မင်းချေပမှုတွေကဒါအကုန်ပဲလားတပဲ့",
    "မင်းချေပမှုတွေကငါအတွက်ရီစရာဖြစ်နေတယ်ဟ",
    "ဘာလိုစာထပ်နေတာလဲပြန်ရေးစမ်း",
    "ဘာလိုစာမှားနေတာလဲPkကြောက်ပြီးလက်တုန်ပြတာလား",
    "ပွဲကြောက်တတ်ရင်ပွဲမရှာနဲ့လေအခုတော့အဆဲခံနေရပြီမှတ်လား",
    "ကျွန်စုတ်လေးရေကူးတာလားရေငုတ်တာလားရေငတ်တာလား",
    "မင်းအရမ်းကောင်းနေလဲဒုတိယပဲရမယ်ခွေးမသားလေး",
    "မင်းလိုအဆင့်နိမ့်သတ္တာဝါကPkဆဲတာပဲခံစမ်း",
    "ကလစ်လေကလေဘာလို့နားနေတာလဲလက်ညောင်းသွားလို့လား",
    "ကလစ်ရင်မင်းမိဘလူတကာဝိုင်းလိုး",
    "အေးတပဲ့မင်းအမေဖာသယ်မ",
    "မင်းအမေဖာသယ်မကြီးနေမကောင်းလို့ဆုံးပြီဆို",
    "မင်းမေဈာပနရှိလို့လိုင်းဆင်းပြေးတာလားကွ",
    "ခွေးတိုးပေါက်ကနေဝင်လာပြီးခွေးတိုးပေါက်ပြေးတာမစမ်းပါဘူးဘောမရ",
    "မင်းအားကိုးလိုရတဲ့ကောင်တွေပါအကုန်ပေးတယ်မင်းအဖေပါဆိုတဲ့ကောင်ပါထက်ပေးတယ်",
    "ဘာလို့နှေးနေတာလဲလိပ်အိုမကြီးသားရ",
    "ပြိုင်ပြောလေဘာလဲသခင်လေးPkနဲ့ယှဉ်မရိုက်နိုင်ဘူးလား",
    "မင်းစာတွေကိုငါစာတွေဖုံးနေပြီမင်းဘယ်လိုလုပ်မလဲ",
    "သခေါမသားမင်းအမေဘာလို့သွားခေါနေရတာ",
    "မင်းမေဝက်မကြီးလူတကာလိုးလို့သေရတာဆို",
    "ဟိတ်ကောငါဂျပုဘယ်ပြေးမှာလဲ",
    "မင်းပြေးတိုင်းလွှတ်ပေးမယ်ထင်နေတာလားသခင်တွေလက်ကလွှတ်ချင်ရင်မင်းအမလာအလိုးခံ",
    "ငယ်ကျွန်လေးသခင်တွေရှေ့မှာခစားစမ်း",
    "ခွေးမသားပိစိလေးဘာလိုရှောက်ကိုက်နေရတာလဲ",
    "ဒီဘိတ်မရလိုငိုတာဆိုငိုစမ်း",
    "စောက်ရူးမသားလေးလာကိုက်လေဘာလိုဂျောင်ထဲမာမာန်ဖီနေရတာလဲ",
    "ဘာလဲဂျောင်ထဲမာကပ်ငိုနေပီလား",
    "မင်းအမေနာရေးရှိလို့ငေးမနေနနဲ့ဆက်ကိုက်ပလိုက်",
    "ဆက်ကိုက်ငါခိုင်းတိုင်းလုပ်တဲ့ကောင်မင်းအမငါလိုး",
    "ဘာလိုမဲမဲမြင်ရာရှောက်ကိုက်ရတာ",
    "မင်းကသခင်တွေမရှိလိုတောင်ပြင်မှာလွှတ်နေတဲ့ခွေးရူးလေးတိုင်းပဲ",
    "လိပ်အိုမကြီးနှေးမနေနဲ့ဆက်ကိုက်",
    "အောက်ထစ်ကခွေးအအမြင့်ကသခင်တွေကိုပြန်ကိုက်ချင်နေတာလား",
    "မင်းဘာလိုပိန်းတိန်းရတာမင်းအမေကပိန်းလို့မျိုးဆက်တူသွားတာလား",
    "မင်းလက်ရေးမလှဘူးပြန်ရေးတပဲ့",
    "မင်းစာတွေထက်မှားပြန်ပြီဘာလဲမင်းအမေပိုက်ဆံမလောက်လို့စာမသင်ပေးခဲ့ဘူးလား",
    "ဆင်းရဲသားသဋေးသားတွေဆဲရင်ခံလေဘာလို့ပြန်တုချင်နေတာလဲ",
    "မင်းအမေကဆင်းရဲလိုဈေးရောင်းနေရတာဆိုဈေးသားမသားလေး",
    "သခင်တွေကလစ်ရင်မင်းမိဘမင်းလိုး",
    "သခင်လေးPkကြမ်းတာမင်းသိပြီလားကွ",
    "သခင်တွေဆီမာမျက်ရည်မျက်ခွပ်နဲ့လာသနားမခံနဲ့ကြက်ဖသခင်တွေကသနားမယ်ထင်လား",
    "ငိုပြမနေနဲ့မင်းအမေဖာသယ်မကြီးသေမှငိုပလိုက်",
    "မင်းအဖေဆိုတဲ့ကောင်ပါပေးတယ်သားပေါက်",
    "တောသီးမင်းကိုအကြော့ပေးရမလား",
    "လွယ်လိုက်တာကွာအနိုင်ယူမိပြန်ပီ",
    "ဟက်ကလစ်ခွေးမင်းကလစ်ကြီးကနှေးကွေးနေတာဘဲTypingဆိုရင်တော့လိပ်ဂွင်းထုမှပြီးမယ့်ကောင်",
    "မင်းဖေ စာတွေမြန်သွားလို့ လိုက်မမှီတော့ဘူးလား",
    "မင်းစောက်သုံးကျသလားဝက်မင်းဘဝကအာမထုရင်းနဲ့အဆုံးသတ်သွားမလား",
    "ဟက်ကလစ်ခွေးမင်းကလစ်ကြီးကနှေးကွေးနေတာဘဲTypingဆိုရင်တော့လိပ်ဂွင်းထုမှပြီးမယ့်ကောင်",
    "ကိုမေကိုလိုးလေး စောက်ခွက်ပိတ်ကန်လိုက်မယ်",
    "စောက်ဆင့်မရှိပဲပြန်ကန်တာဟုတ်လား",
    "ဘာငိုရမှာလဲမင်းအမေသေလို့ငိုရမာလား",
    "မင်းမာဖုန်းစုတ်လေးပြင်ပီးမှငါနဲ့  ယှဥ်ငတိရ",
    "မင်းငါ့စကေးကြောင့်လက်တုန်နေပီရေသောက်ပီမှပြန်ရိုက်မယ်",
    "ဘာတွေရှင်းပြချင်တာ မင်းမေဈပနအတွက်ပိုက်ဆံမလောက်လို့လား",
    "မှော်ဆန်တဲ့ရိုက်ချက်တွေကြားအလူလဲခံနေရပြီလားဖာသည်မသား",
    "ဘာတွေဟောင်ပြနေတာ ခွေး ဆက်ကိုက်လေ",
    "ငါဆဲတာမမှတ်လို့ လာအဆဲခံတာလား",
    "ငါ့အမိန့်မရပဲဘာကိုနားချင်တာလဲခွေးမသားမျိုး",
    "စောက်ရူးမသား မွေးလာကတည်းကကျပ်မပြည့်တာဆို",
    "ဘာတွေရိုက်ပြနေတာလဲ ဝက်မ ဆက်ရိုက်ထား နားရင်သေမယ်",
    "ဆင်းရဲသားလေးမင်းအမေကဖာသယ်မလုပ်ပီးရှာကျွေးနေတာဆို",
    "တောသား အညာသူမသားတတ်နေလား တတ်နေရင်မင်းမေကျွန်မထက်လိုးပြ",
    "မေလိုးစာကမှားသေး ငါနဲ့ယှဉ်ရိုက်ရလို့လက်တုန်နေတာလာ အေးတပံ ဆျာခွင့်လွှတ်တယ် စာရိုက်ရလို့လက်နာနေတာလား နာနေတဲ့လက်မင်းမေဖင်ထဲထိုးထည့်",
    "မင်းစာရိုက်နေတာလား ငါဖုန်းထဲမှာခွေးလေးရေးထားသလို့ပဲဟ",
    "စောက်ပိန်းဖစ်ထွန်းမရှိပဲနဲ့ငါတို့နဲ့ယှဉ်ချင်တာလာ"
]

# ====== VARIABLES ======
targets = {}            # For Auto Reply
auto_mentions = {}      # For Auto Mention
auto_deletes = {}       # {chat_id: {user_id1, user_id2, ...}}
mention_delay = 30      # default 30 seconds
reply_index = 0
mention_index = 0
BOT_RUNNING = True      # Bot Status Control

# ====== TELETHON CLIENT ======
client = TelegramClient("userbot", api_id, api_hash)

# ====== HELPERS ======
def is_owner(user_id):
    return user_id in MAIN_OWNER

async def log_to_owner(msg):
    print(msg)
    for owner_id in MAIN_OWNER:
        try:
            await client.send_message(owner_id, f"🪵 {msg}")
        except:
            pass

async def is_admin(chat_id, user_id):
    try:
        # Check if the chat is a channel/group and if the user is an admin
        participants = await client.get_participants(chat_id, filter=ChannelParticipantsAdmins)
        return any(p.id == user_id for p in participants)
    except Exception:
        # Assume not admin or not a group/channel if check fails
        return False

# ====== Typing Indicator ======
async def show_typing(chat_id, duration):
    start = time.time()
    while time.time() - start < duration:
        try:
            async with client.action(chat_id, 'typing'):
                await asyncio.sleep(3)
        except Exception as e:
            print(f"[TypingError] {e}")
            break

# ----------------------------------------------------------------------
#                         NEW COMMAND IMPLEMENTATION (Owner Only)
# ----------------------------------------------------------------------

# ====== BOT CONTROL (Owner Only) ======
@client.on(events.NewMessage(pattern=r"^/stopbot$"))
async def stop_bot_handler(event):
    global BOT_RUNNING
    sender = await event.get_sender()
    if not is_owner(sender.id):
        return
    
    BOT_RUNNING = False
    # Send a visible message to the chat that the bot is stopping
    await event.reply("🔴 Bot is stopping...") 
    await log_to_owner("🔴 Userbot Stopped by Owner.")
    # Stop the client after a short delay to allow the reply to send
    await asyncio.sleep(1)
    await client.disconnect()

@client.on(events.NewMessage(pattern=r"^/startbot$"))
async def start_bot_handler(event):
    global BOT_RUNNING
    sender = await event.get_sender()
    if not is_owner(sender.id):
        return
    
    if not BOT_RUNNING:
        BOT_RUNNING = True
        # Send a visible message to the chat that the bot has started
        await event.reply("🟢 Bot started. Running background tasks.")
        await log_to_owner("🟢 Userbot Started by Owner.")
    else:
        # Only log to owner if bot is already running
        await log_to_owner("⚠️ Bot is already running.") 

# ====== COMMON (Owner Only - Except /getid, /help) ======
@client.on(events.NewMessage(pattern=r"^/getid$"))
async def get_id_handler(event):
    chat_id = event.chat_id
    user = await event.get_sender()
    user_id = user.id
    
    reply_text = f"👤 User ID: `{user_id}`\n"
    reply_text += f"💬 Chat ID: `{chat_id}`"
    
    # This command must reply in the group/chat to be useful
    await event.reply(reply_text, parse_mode='markdown')

@client.on(events.NewMessage(pattern=r"^/help$"))
async def help_handler(event):
    help_menu = """
**🚀 Userbot Command Menu 🚀**

**BOT CONTROL (Owner Only):**
• `/stopbot` - Stop the bot.
• `/startbot` - Resume bot activities.

**COMMON:**
• `/getid` - Get your User ID and the Chat ID.
• `/help` - Display this menu.

**AUTO-DELETE (Owner Only):**
• Reply with `/ကန်` to a user's message to enable auto-delete for them in this chat.
• `/autodelete @user` - Enable auto-delete for specified user.
• `/stopautodelete @user` - Disable auto-delete for that user.
• `/stopautodelete` - Disable auto-delete for ALL users in this chat.

**AUTO-MENTION (Owner Only):**
• `/listmentions` - Show users currently being auto-mentioned in this chat.
• `/stopmention (reply)` - Stop auto-mention for a specific user.
• `/stopmention` - Stop ALL auto-mentions in this chat.
• `/stopallmentions` - Stop ALL auto-mentions globally (all chats).
• `/setmentioninterval [seconds]` - Set the mention interval (5-3600s).

**EXISTING AUTO-REPLY (Owner Only):**
• **Start**: Reply with `ဟျောင့်ဝက်မကိုက်လေ` (or similar triggers) to a message.
• **Stop**: Reply with `သေလိုက်` to a target's message, or send it alone to clear all targets.
"""
    # This command must reply in the group/chat to be useful
    await event.reply(help_menu, parse_mode='markdown')

# ====== AUTO-DELETE IMPLEMENTATION (Owner Only) ======
# Listener for /ကန် (Reply)
@client.on(events.NewMessage(pattern=r"^/ကန်$"))
async def enable_autodelete_reply(event):
    sender = await event.get_sender()
    if not is_owner(sender.id):
        # Changed to Owner Only
        return await event.reply("🚨 You must be an owner to use this command.")

    if event.is_reply:
        reply_msg = await event.get_reply_message()
        user_to_delete = await reply_msg.get_sender()
        
        chat_id = event.chat_id
        user_id = user_to_delete.id

        if chat_id not in auto_deletes:
            auto_deletes[chat_id] = set()
        
        auto_deletes[chat_id].add(user_id)
        
        await log_to_owner(f"[AutoDelete] Enabled for {user_id} in {chat_id} via /ကန်")

    else:
        # Keep instruction reply in the group
        await event.reply("⚠️ Please reply to a user's message with `/ကန်` to enable auto-delete for them.")

# Listener for /autodelete @user
@client.on(events.NewMessage(pattern=r"^/autodelete\s+(@\w+|\d+)$"))
async def enable_autodelete_mention(event):
    sender = await event.get_sender()
    if not is_owner(sender.id):
        # Changed to Owner Only
        return await event.reply("🚨 You must be an owner to use this command.")

    match = re.match(r"^/autodelete\s+(@\w+|\d+)$", event.raw_text)
    user_identifier = match.group(1)
    
    try:
        user_entity = await client.get_entity(user_identifier)
        user_id = user_entity.id
        chat_id = event.chat_id

        if chat_id not in auto_deletes:
            auto_deletes[chat_id] = set()
        
        auto_deletes[chat_id].add(user_id)
        
        await log_to_owner(f"[AutoDelete] Enabled for {user_id} in {chat_id} via mention/ID")

    except Exception as e:
        # Keep error reply in the group
        await event.reply(f"❌ Could not find user: {user_identifier}")
        await log_to_owner(f"[AutoDeleteError] {e}")


# Listener for /stopautodelete @user
@client.on(events.NewMessage(pattern=r"^/stopautodelete\s+(@\w+|\d+)$"))
async def disable_autodelete_mention(event):
    sender = await event.get_sender()
    if not is_owner(sender.id):
        # Changed to Owner Only
        return await event.reply("🚨 You must be an owner to use this command.")

    match = re.match(r"^/stopautodelete\s+(@\w+|\d+)$", event.raw_text)
    user_identifier = match.group(1)
    chat_id = event.chat_id

    try:
        user_entity = await client.get_entity(user_identifier)
        user_id = user_entity.id

        if chat_id in auto_deletes and user_id in auto_deletes[chat_id]:
            auto_deletes[chat_id].remove(user_id)
            if not auto_deletes[chat_id]:
                del auto_deletes[chat_id]

            await log_to_owner(f"✅ Auto-delete DISABLED for user {user_id} in chat {chat_id}")
        else:
            # Keep informational reply in the group
            await event.reply(f"User `{user_id}` was not on the auto-delete list.")

    except Exception as e:
        # Keep error reply in the group
        await event.reply(f"❌ Could not find user: {user_identifier}")
        await log_to_owner(f"[AutoDeleteError] {e}")


# Listener for /stopautodelete (All)
@client.on(events.NewMessage(pattern=r"^/stopautodelete$"))
async def disable_autodelete_all(event):
    sender = await event.get_sender()
    if not is_owner(sender.id):
        # Changed to Owner Only
        return await event.reply("🚨 You must be an owner to use this command.")
    
    chat_id = event.chat_id
    if chat_id in auto_deletes:
        del auto_deletes[chat_id]
        await log_to_owner(f"🚫 Auto-delete DISABLED for ALL users in chat {chat_id}")
    else:
        # Keep informational reply in the group
        await event.reply("No active auto-delete users in this chat.")

# Message deletion logic (remains silent)
@client.on(events.NewMessage)
async def delete_target_message(event):
    if not BOT_RUNNING:
        return
        
    chat_id = event.chat_id
    sender = await event.get_sender()
    
    if chat_id in auto_deletes and sender.id in auto_deletes[chat_id]:
        try:
            await event.delete()
        except Exception as e:
            await log_to_owner(f"[DeleteError] Could not delete message from {sender.id} in {chat_id}: {e}")

# ====== AUTO-MENTION COMMANDS (Owner Only) ======
# Helper to check if a user is being auto-mentioned in a specific chat
def is_user_mentioning(chat_id, user_id):
    return chat_id in auto_mentions and user_id in auto_mentions[chat_id]

@client.on(events.NewMessage(pattern=r"^/listmentions$"))
async def list_mentions_handler(event):
    sender = await event.get_sender()
    if not is_owner(sender.id):
        return
        
    chat_id = event.chat_id
    
    if chat_id in auto_mentions and auto_mentions[chat_id]:
        mentions = "\n".join([f"• ID `{uid}` (Nickname: {nickname})" for uid, nickname in auto_mentions[chat_id].items()])
        # Keep this list in the group/chat since it's informational for the owner
        await event.reply(f"🎯 Users currently being auto-mentioned in this chat:\n\n{mentions}", parse_mode='markdown')
    else:
        await event.reply("No users are currently set for auto-mention in this chat.")

# /stopmention (reply and general)
@client.on(events.NewMessage(pattern=r"^/stopmention$"))
async def stop_mention_handler(event):
    sender = await event.get_sender()
    if not is_owner(sender.id):
        return

    chat_id = event.chat_id
    
    if event.is_reply:
        # Case 1: Stop mention for a specific user (reply)
        reply_msg = await event.get_reply_message()
        user_to_stop = await reply_msg.get_sender()
        user_id = user_to_stop.id

        if is_user_mentioning(chat_id, user_id):
            del auto_mentions[chat_id][user_id]
            if not auto_mentions[chat_id]:
                del auto_mentions[chat_id]
            await log_to_owner(f"[AutoMention] Stopped for {user_id} in {chat_id}")
        else:
            await event.reply("That user is not currently being auto-mentioned here.")
    else:
        # Case 2: Stop all mentions in the current chat
        if chat_id in auto_mentions and auto_mentions[chat_id]:
            del auto_mentions[chat_id]
            await log_to_owner(f"[AutoMention] All stopped in chat {chat_id}")
        else:
            await event.reply("No active auto-mentions in this chat.")

# /stopallmentions (global)
@client.on(events.NewMessage(pattern=r"^/stopallmentions$"))
async def stop_all_mentions_handler(event):
    sender = await event.get_sender()
    if not is_owner(sender.id):
        return

    global auto_mentions
    if auto_mentions:
        count = len(auto_mentions)
        auto_mentions = {}
        await log_to_owner(f"[AutoMention] All stopped globally. Cleared mentions from {count} chats.")
    else:
        await event.reply("No active auto-mentions globally.")

# /setmentioninterval [seconds]
@client.on(events.NewMessage(pattern=r"^/setmentioninterval\s+(\d+)$"))
async def set_mention_interval_handler(event):
    global mention_delay
    sender = await event.get_sender()
    if not is_owner(sender.id):
        return
    
    match = re.match(r"^/setmentioninterval\s+(\d+)$", event.raw_text)
    if match:
        new_delay = int(match.group(1))
        
        # Enforce range 5-3600
        if 5 <= new_delay <= 3600:
            mention_delay = new_delay
            await log_to_owner(f"⏱ Auto Mention delay updated to {mention_delay} seconds")
        else:
            await event.reply("⚠️ Interval must be between 5 and 3600 seconds.")

# ----------------------------------------------------------------------
#                         EXISTING QT.PY HANDLERS (All Owner Only)
# ----------------------------------------------------------------------

# ====== ADD AUTO REPLY TARGET (Original) ======
@client.on(events.NewMessage(pattern=r"^(ဟျောင့်ဝက်မကိုက်လေ|မင်းပါဝင်ကိုက်|အဲတာဆိုကိုက်|နာနာကိုက်ပါလားဘောမ|ဟျောင့်ဘောမကိုက်လေ|ဟျောင့်ဝက်ပုသေချာကိုက်ထား)$"))
async def add_target(event):
    if not BOT_RUNNING: return
    sender = await event.get_sender()
    if not is_owner(sender.id):
        return
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        user = await reply_msg.get_sender()
        chat_id = event.chat_id
        targets[user.id] = {"chat": chat_id, "last_msg": None, "last_replied": None}
        await log_to_owner(f"[+] Auto Reply Started for {user.first_name} ({user.id}) in chat {chat_id}")
    else:
        await event.reply("⚠️ Reply to a message to set an auto-reply target.")

# ====== STOP AUTO REPLY (Original) ======
@client.on(events.NewMessage(pattern=r"^သေလိုက်$"))
async def stop_target(event):
    if not BOT_RUNNING: return
    sender = await event.get_sender()
    if not is_owner(sender.id):
        return
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        user = await reply_msg.get_sender()
        if user.id in targets:
            del targets[user.id]
            await log_to_owner(f"[*] Stopped Auto Reply for {user.first_name} ({user.id})")
    else:
        targets.clear()
        await log_to_owner("[*] All Auto Reply Targets Cleared")

# ====== CATCH TARGET MESSAGES (Original) ======
@client.on(events.NewMessage)
async def catch_target_message(event):
    if not BOT_RUNNING: return
    sender = await event.get_sender()
    if sender.id in targets:
        targets[sender.id]["last_msg"] = event.message

# ====== ADD AUTO MENTION (Original) ======
@client.on(events.NewMessage)
async def add_auto_mention(event):
    if not BOT_RUNNING: return
    sender = await event.get_sender()
    if not is_owner(sender.id):
        return
    if event.is_reply and event.raw_text.startswith("123 ဖာသည်မသား"):
        match = re.match(r"123 ဖာသည်မသား (.+)", event.raw_text)
        if match:
            nickname = match.group(1)
            reply_msg = await event.get_reply_message()
            user = await reply_msg.get_sender()
            chat_id = event.chat_id
            
            if not getattr(user, 'username', None) and not user.first_name:
                await event.reply("⚠️ Cannot mention this user. They must have a username or first name.")
                return

            if chat_id not in auto_mentions:
                auto_mentions[chat_id] = {}
            auto_mentions[chat_id][user.id] = nickname
            await log_to_owner(f"[+] Auto Mention Added: {nickname} ({user.id}) in chat {chat_id}")

# ====== STOP AUTO MENTION (Original) ======
@client.on(events.NewMessage(pattern=r"^သေပြီလား$"))
async def stop_auto_mention_original(event):
    if not BOT_RUNNING: return
    sender = await event.get_sender()
    if not is_owner(sender.id):
        return
    chat_id = event.chat_id
    if chat_id in auto_mentions and auto_mentions[chat_id]:
        auto_mentions[chat_id].clear()
        del auto_mentions[chat_id]
        await log_to_owner(f"[x] Auto Mention stopped in chat {chat_id}")
    else:
        await event.reply(f"⚠️ No active mentions found in this chat.")

# ====== SET MENTION DELAY (Original) ======
@client.on(events.NewMessage(pattern=r"^/setsecmention (\d+)$"))
async def set_mention_delay_original(event):
    global mention_delay
    sender = await event.get_sender()
    if not is_owner(sender.id):
        return
    match = re.match(r"^/setsecmention (\d+)$", event.raw_text)
    if match:
        new_delay = int(match.group(1))
        if 5 <= new_delay <= 3600:
            mention_delay = new_delay
            await log_to_owner(f"⏱ Auto Mention delay updated to {mention_delay} seconds (Original command)")
        else:
            await event.reply("⚠️ Interval must be between 5 and 3600 seconds.")

# ----------------------------------------------------------------------
#                         LOOP FUNCTIONS (Original)
# ----------------------------------------------------------------------

# ====== AUTO REPLY LOOP ======
async def auto_reply_loop():
    global reply_index
    while True:
        if not BOT_RUNNING:
            await asyncio.sleep(5)
            continue
            
        try:
            for uid, data in list(targets.items()):
                if data["last_msg"] and (data["last_replied"] != data["last_msg"].id):
                    await show_typing(data["chat"], 5)

                    if auto_replies:
                        reply_text = auto_replies[reply_index]
                        reply_index = (reply_index + 1) % len(auto_replies)
                    else:
                        reply_text = "🤖 Auto reply active!"
                        
                    # Ensure the chat and message still exist before replying
                    try:
                        await client.send_message(data["chat"], reply_text, reply_to=data["last_msg"].id)
                        data["last_replied"] = data["last_msg"].id
                        # Auto-reply message log removed as requested
                    except Exception as send_e:
                        await log_to_owner(f"[AutoReplySendError] Failed to send to {uid}: {send_e}. Removing target.")
                        del targets[uid] # Remove target if sending fails

            await asyncio.sleep(1)
        except Exception as e:
            await log_to_owner(f"[AutoReplyLoopError] {e}")
            await asyncio.sleep(3)

# ====== AUTO MENTION LOOP ======
async def mention_loop():
    global mention_index
    while True:
        if not BOT_RUNNING:
            await asyncio.sleep(5)
            continue

        try:
            for chat_id, users in list(auto_mentions.items()):
                if not users:
                    # Clean up empty chat entry
                    del auto_mentions[chat_id]
                    continue

                await show_typing(chat_id, 5)

                lines = []
                for uid, nickname in list(users.items()):
                    
                    if auto_replies:
                        msg = auto_replies[mention_index]
                        mention_index = (mention_index + 1) % len(auto_replies)
                    else:
                        msg = "👋 Hey!"

                    try:
                        user_entity = await client.get_entity(uid)
                        # Prefer @username if available, otherwise use a markdown mention link
                        mention_text = f"@{user_entity.username}" if getattr(user_entity, "username", None) else f"[{nickname}](tg://user?id={uid})"
                    except Exception as e:
                        # Fallback for users not found
                        mention_text = f"[{nickname}](tg://user?id={uid})"
                        await log_to_owner(f"[MentionEntityError] {uid}: {e}")

                    lines.append(f"{mention_text}\n{msg}")

                text = "\n\n".join(lines)
                
                try:
                    await client.send_message(chat_id, text, parse_mode="markdown")
                    # Auto-mention message log removed as requested
                except Exception as send_e:
                    await log_to_owner(f"[MentionSendError] Failed to send in {chat_id}: {send_e}. Removing chat from mentions.")
                    del auto_mentions[chat_id] # Stop mentioning if sending fails

            await asyncio.sleep(mention_delay) # Uses the global mention_delay
        except Exception as e:
            await log_to_owner(f"[MentionLoopError] {e}")
            await asyncio.sleep(5)

# ====== FLASK KEEP ALIVE ======
app = Flask('')

@app.route('/')
def home():
    return "Userbot is alive ✅"

def run_web():
    app.run(host='0.0.0.0', port=3000)

Thread(target=run_web).start()

# ====== MAIN ======
async def main():
    await client.start()
    await log_to_owner("✅ Userbot Started (Sequential Auto Reply + Auto Mention + New Features)")
    asyncio.create_task(auto_reply_loop())
    asyncio.create_task(mention_loop())
    await client.run_until_disconnected()

# Check if bot status is running before running main loop
if BOT_RUNNING:
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Main execution failed: {e}")
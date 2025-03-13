import os
import subprocess
import sys
from datetime import datetime
import time
import requests

# التحقق من وجود المكتبات المطلوبة وتثبيتها إذا لزم الأمر
def install_libraries():
    required_libraries = ["geopy", "plyer", "praytimes", "winshell", "pywin32", "requests"]
    for lib in required_libraries:
        try:
            __import__(lib)
            print(f"المكتبة {lib} مثبتة بالفعل.")
        except ImportError:
            print(f"جاري تثبيت المكتبة {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# تثبيت المكتبات المطلوبة
install_libraries()

# الآن يمكن استيراد المكتبات بأمان
from geopy.geocoders import Nominatim
from plyer import notification
from praytimes import PrayTimes
import winshell
from win32com.client import Dispatch

# 1. تحديد الموقع الجغرافي تلقائيًا
def get_location():
    geolocator = Nominatim(user_agent="prayer_times_app")
    location = geolocator.geocode("")  # تحديد الموقع الحالي
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

# 2. حساب مواقيت الصلاة
def calculate_prayer_times(latitude, longitude, timezone):
    pt = PrayTimes()
    pt.setMethod('MWL')
    date = datetime.now().timetuple()[:3]  # التاريخ الحالي
    prayer_times = pt.getTimes(date, (latitude, longitude), timezone)
    return prayer_times

# 3. إرسال إشعارات
def send_notification(prayer_name, prayer_time):
    notification.notify(
        title=f"موعد صلاة {prayer_name}",
        message=f"حان وقت صلاة {prayer_name} على الساعة {prayer_time}",
        timeout=10
    )

# 4. حفظ المواقيت في ملف نصي
def save_to_file(prayer_times, filename="prayer_times.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        for name, time in prayer_times.items():
            file.write(f"{name}: {time}\n")

# 5. تشغيل البرنامج تلقائيًا عند بدء تشغيل ويندوز
def add_to_startup():
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    if not os.path.exists(startup_folder):
        os.makedirs(startup_folder)
    script_path = os.path.abspath(__file__)
    shortcut_path = os.path.join(startup_folder, "PrayerTimesApp.lnk")
    
    if not os.path.exists(shortcut_path):
        try:
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = script_path
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.save()
            print("تمت إضافة البرنامج إلى بدء التشغيل.")
        except Exception as e:
            print(f"حدث خطأ أثناء إضافة البرنامج إلى بدء التشغيل: {e}")

# 6. التحقق من التحديثات على GitHub
def check_for_updates():
    repo_owner = "your_github_username"  # استبدل باسم مستخدم GitHub الخاص بك
    repo_name = "your_repo_name"  # استبدل باسم المستودع الخاص بك
    current_version = "1.0.0"  # الإصدار الحالي للبرنامج

    try:
        # الحصول على آخر إصدار من GitHub API
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        response = requests.get(url)
        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release["tag_name"]

            if latest_version != current_version:
                print(f"يوجد تحديث جديد: الإصدار {latest_version}")
                print("يرجى زيارة المستودع لتنزيل التحديث.")
                print(f"رابط المستودع: https://github.com/{repo_owner}/{repo_name}")
            else:
                print("أنت تستخدم أحدث إصدار.")
        else:
            print("تعذر التحقق من التحديثات. يرجى المحاولة لاحقًا.")
    except Exception as e:
        print(f"حدث خطأ أثناء التحقق من التحديثات: {e}")

# البرنامج الرئيسي
if __name__ == "__main__":
    # التحقق من التحديثات
    check_for_updates()
    
    # إضافة البرنامج إلى بدء التشغيل
    add_to_startup()
    
    # تحديد الموقع الجغرافي
    location = get_location()
    if location:
        latitude, longitude = location
        timezone = 2  # التوقيت المحلي (UTC+2)
        prayer_times = calculate_prayer_times(latitude, longitude, timezone)
        
        # عرض المواقيت
        for name, time in prayer_times.items():
            print(f"{name}: {time}")
        
        # إرسال إشعارات
        for name, time in prayer_times.items():
            send_notification(name, time)
            time.sleep(1)  # تأخير بين الإشعارات
        
        # حفظ المواقيت في ملف نصي
        save_to_file(prayer_times)
    else:
        print("تعذر تحديد الموقع الجغرافي.")

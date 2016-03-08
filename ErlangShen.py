#-*-coding utf-8 -*-
import re
import string
import datetime
import time
import os
import sys
import getopt
import xml.etree.ElementTree as et
import multiprocessing
from tools import Color
clr = Color()
AAPT = os.path.join(os.getcwd(),'tools\\aapt.exe')

def get_devices_list():   

	adb_list = re.findall(r'([a-zA-Z0-9]+)\t+device',os.popen("adb devices").read().strip())
	return adb_list

def get_apk_list(apkSrc):
    """
    Get all apk packages
    """
    if not os.path.exists(apkSrc):
        print "%s isn't exists"
    else:
        return os.popen('dir /b %s | findstr  ".apk"'%apkSrc).read().strip().split('\n')

def get_apk_src():

    """
    Append all apks list like:
    ['\\\\cntds-server\\docs\\apks\\com.baidu.appsearch_035041.apk',
    '\\\\cntds-server\\docs\\apks\\com.estrongs.android.pop_501.apk']
    """
    tree = et.parse('path_config.xml')
    root = tree.getroot()
    apk_src = root.find('apkSrc').findall('path')
    return [os.path.join(src,apk) for src in [src.get('name') for src in apk_src] for apk in get_apk_list(src)]

def generate_apk_info(apk_path):
        print "generate %s info "%os.path.split(apk_path)[-1] 
        command = AAPT + ' dump badging %s'%apk_path
        try:
            info = os.popen(command).read().strip()
            pkg_name = re.findall("package: name='(\S*)'",info)[0]
            launchable_activity = re.findall("launchable-activity: name='(\S*)'",info)[0]
        except IndexError as e:
            print "generate apk info failed" + str(e) + "\n Please update the %s"%os.path.split(apk_path)[-1]  
            return False
        if pkg_name and launchable_activity:
            return pkg_name,launchable_activity
    

def deco_test_result(func):
    def wrapper(*args,**kw):
        result = func(*args,**kw)
        if re.search("Success",result):
            print "Test %s success"%func.__name__ 
        elif re.search('Fail',result):
            print "Test %s fail"%func.__name__
    return wrapper

def write_result_to_devicetxt(device,result,time_stamp):
    with file("log\ErLangShen_%s_%s.json"%(device,time_stamp),"a") as f:
        f.write(result)

def init_report(device_wtih_timestamp):
    css = """<style>
table {border-collapse: collapse;}
td, th {border:1px solid #aaaaaa;padding:4px;}
th {font: bold 1em; background: #bfbfff; text-align:center}
span {padding: 4px;margin: 4px;}
.pass {color: #2db300;text-align:center}
.fail {color: #ff2626;text-align:center}
.warning {color: #ff9326;text-align:center}
.failure_desc {background: #dfdfd0; color: red;}
.slogon {margin-top:50px;color:#888888}
</style>"""
    title = """<h2>ErLangShen Test Report</h2>
<p>- 3rdparty APP test automation by PDT -</p>
<hr style='width: 300px;text-align:left'>
</div>"""
    category = """<table style="width:1200px;margin-top:40px;">
    <tr><th>Index</th><th>APP</th><th>Install</th><th>Launch</th><th>Monkey</th><th>Uninstall</th><th>Compatibility Conclusion</th></tr>"""

    with file("report\%s.html"%device_wtih_timestamp,"w") as f:
        f.write(css+"\n") 
        f.write(title+"\n")
        f.write(category+"\n")


def test_install_apk(device,apk_path,time_stamp):

    print "start install app %s for %s"%(os.path.split(apk_path)[-1],device)
    install_result = os.popen("adb -s %s install -r %s"%(device,apk_path)).read().strip().encode('utf8')
    if install_result.find("Success") != -1:
        print "install %s successfully"%os.path.split(apk_path)[-1]
        write_result_to_devicetxt(device,'{"%s":{"Install":"Pass",'%os.path.split(apk_path)[-1],time_stamp)
        return True
    else:
        print "install fail"
        write_result_to_devicetxt(device,'{"%s":{"Install":"Failed %s",'%(os.path.split(apk_path)[-1],install_result.split("\n")[-1]),time_stamp)
        return False


def test_launch_apk(device,pkg_name,launchable_activity,time_stamp):
    
    print "start launch %s"%pkg_name
    command = 'adb -s %s shell am start -n %s/%s '%(device,pkg_name,launchable_activity)
    clr.print_blue_text(command)
    launchable_result = os.popen(command).read().strip().encode('utf8')
    print "wait 3s for device launch app "
    time.sleep(3)

    if launchable_result.find("Error") != -1:
        print "Launch %s failed "%pkg_name,launchable_result
        write_result_to_devicetxt(device,'"Launch":"Failed %s",'%launchable_result[launchable_result.find("Error"):launchable_result.find("Error")+12],time_stamp)
        return False
    
    ps_check_command = 'adb -s %s shell "ps | grep %s"'%(device,pkg_name)
    clr.print_blue_text("Check app launched or not by command %s\n"%ps_check_command)
    ps_check = os.popen(ps_check_command).read().strip()
    print ps_check
    if len(ps_check) < len(ps_check_command):
        print "launch %s failed"%pkg_name
        write_result_to_devicetxt(device,'"Launch":"Fail reason couldn\'t be found.",',time_stamp)
        return False
    else :
        print "lanch successfully"
        write_result_to_devicetxt(device,'"Launch":"Pass",',time_stamp)
        return True



def test_monkey_run(device,pkg_name,time_stamp):
    
    print "start monkey test on %s "%pkg_name
    command = 'adb -s %s shell monkey -p %s -v -v -v --throttle 500 200'%(device,pkg_name)
    clr.print_blue_text(command+'\n')
    monkey_result = os.popen(command).read().strip().encode('utf8')
    if monkey_result.find("Monkey finished") != -1:
        print "Monkey tests successfully"
        write_result_to_devicetxt(device,'"Monkey":"Pass",',time_stamp)
        return True
    else :
        reason_filter = ''
        for line in monkey_result.split("\n"):
            if re.match("// CRASH:",line) or re.search("NOT RESPONDING:"):
                reason_filter = reason_filter + line +" "
        clr.print_red_text(reason_filter)
        write_result_to_devicetxt(device,'"Monkey":"Fail %s",'%reason_filter.replace('\n',' '),time_stamp)
        print "Monkey tests had errors "
        return False


def test_uninstall_apk(device,pkg_name,time_stamp):
    
    print "uninstall %s app "%pkg_name
    uninstall_result = os.popen('adb -s %s uninstall %s'%(device,pkg_name)).read().strip().encode('utf8')
    if uninstall_result.find("Success") != -1:
        print "Uninstall app successfully" 
        write_result_to_devicetxt(device,'"Uninstall":"Pass"}}\n',time_stamp)
        return True
    else :
        write_result_to_devicetxt(device,'"Uninstall":"Failed %s"}}\n'%uninstall_result,time_stamp)
        print "Uninstall_result app failed"
        return False


def main():

    global apk_info
    global log_path 
    global time_stamp
    time_stamp = time.strftime("%m%d%Y_%H.%M.%S", time.localtime())

    for device in get_devices_list():
        report_path= "ErLangShen_Report_%s_%s"%(device,time_stamp)
        init_report(report_path)


    ErlangShen_weapons = {"install" : test_install_apk,\
                          "launch"  : test_launch_apk,\
                          "monkey"  : test_monkey_run,\
                          "uninstall" : test_uninstall_apk}

    try:
        for apk in get_apk_src():
            task_len = len(get_devices_list())

            if task_len == 0:
                print "No device connected or devices offline"
                break  

            apk_info = generate_apk_info(apk)


            if not apk_info:
                continue

            if task_len:
                clr.print_blue_text("*** %d device(s) connected ***"%task_len)
                for weapon in sorted(ErlangShen_weapons.keys()):
                    if weapon == "install":
                        clr.print_green_text("ErlangShen would spaw %d %s process(es) to test %s on all devices"%(task_len, weapon, os.path.split(apk)[-1]))
                        pool = multiprocessing.Pool(processes=task_len)
                        for device in get_devices_list():
                            pool.apply_async(ErlangShen_weapons[weapon],(device,apk,time_stamp))
                        pool.close()
                        pool.join()

                    if weapon == "launch":
                        clr.print_green_text("ErlangShen would spaw %d %s process(es) to test %s on all devices"%(task_len, weapon, os.path.split(apk)[-1]))
                        pool = multiprocessing.Pool(processes=task_len)
                        for device in get_devices_list():
                            pool.apply_async(ErlangShen_weapons[weapon],(device,apk_info[0],apk_info[1],time_stamp,))
                        pool.close()
                        pool.join()
                    
                    if weapon == "monkey":
                        clr.print_green_text("ErlangShen would spaw %d %s process(es) to test %s on all devices"%(task_len, weapon, os.path.split(apk)[-1]))
                        pool = multiprocessing.Pool(processes=task_len)
                        for device in get_devices_list():
                            pool.apply_async(ErlangShen_weapons[weapon],(device,apk_info[0],time_stamp,))
                        pool.close()
                        pool.join()
                    
                    if weapon == "uninstall":
                        clr.print_green_text("ErlangShen would spaw %d %s process(es) to test %s on all devices"%(task_len, weapon, os.path.split(apk)[-1]))
                        pool = multiprocessing.Pool(processes=task_len)
                        for device in get_devices_list():
                            pool.apply_async(ErlangShen_weapons[weapon],(device,apk_info[0],time_stamp,))
                        pool.close()
                        pool.join()

            else:
                clr.print_red_text("No device connected")       

    except Exception as e:
        print "[Exception]" + str(e) 
    finally:
        #os.system("move log\*.json %s"%log_path)
        sys.exit()
        

if __name__ == '__main__':
    main()
    
    

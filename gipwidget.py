#!/usr/bin/python3
from lib import g, myio, mylaunch
import os, socket, subprocess

proxy= 'http://127.0.0.1:8118'
modemstatus_url= 'http://192.168.1.254/cgi-bin/broadbandstatistics.ha'

font=('Courier', 14);  bg= '#ffe';  bigfont=('Courier Bold', 14)

class Fmain(g.packframe):
  def populate(self):
    self.configure(bg= bg)
    gr= self.gr= self.gridf(2, bg= bg)
    self.vlocalip= g.stringvar()
    self.pop_var('Local IP:', self.vlocalip, ofont= bigfont)
    self.vlocalipv6= g.stringvar()
    self.pop_var('Local IPv6:', self.vlocalipv6)
    self.vglobalip= g.stringvar();  self.vglobalname= g.stringvar()
    self.pop_var('Global IP:', self.vglobalip)
    self.pop_var('Hostname:', self.vglobalname)
    self.vtorip= g.stringvar();  self.vtorip.set('refresh to see')
    self.pop_var('Tor IP:', self.vtorip)

    cr= self.ctlrow(bg= bg)
    cr.button(text= 'Refresh',      command= self.refresh)
    cr.button(text= 'Ping',         command= self.ping)
    cr.button(text= 'Modem status', command= self.modemstatus)
    cr.button(text= 'WICD',         command= self.wicd)
    cr= self.ctlrow(bg= bg);  cr.label('Daemon restarts:', bg= bg)
    cr.button(text= 'TOR RESTART',    command= self.tor_restart)
    cr.button(text= 'Privoxy',        command= self.privoxy_daemon)
    cr.button(text= 'WICD daemon',    command= self.wicd_daemon)
    cr.button(text= 'Network daemon', command= self.network_daemon)
    self.get_misc()

  def pop_var(self, ltext, var, ofont= None): 
    if not ofont:  ofont= font
    gr= self.gr;   gr.label(ltext, bg= bg);  gr.varlabel(var, font= ofont, bg= bg)

  def modemstatus(self):  mylaunch.launchurl(modemstatus_url, proxy= 0)
  def refresh(self):      self.get_misc();  self.get_torip()

  def get_misc(self):
    g.update_main()
    self.local_ip= self.local_ipv6= '???'
    self.get_local_ip();  local_ip= self.local_ip
    if not local_ip:
      self.vglobalip.set('???')
      self.title('Something wrong with connection')
      g.update_main();  return
    self.vlocalip.set(local_ip);  self.vlocalipv6.set(self.local_ipv6);
    self.title('IP '+ local_ip);  g.update_main()
    global_ip= myio.global_ip()
    if global_ip:
      global_hostname= hostname_from_ip(global_ip)
      self.vglobalip.set(global_ip);  self.vglobalname.set(global_hostname)
    g.update_main()

  def get_local_ip(self):
    with os.popen('/sbin/ifconfig | grep "inet"') as pse:
      for line in pse:
        if '127.0.0.' in line:  continue
        if '::1'      in line:  continue
        line= line.replace('addr:', '') # not all ifconfigs are the same
        if 'inet ' in line:
          line= line.replace('inet ', '')
          line= line.lstrip();  i = line.find(' ')
          if i< 0:  self.local_ip= line
          else:     self.local_ip= line[:i]
        if 'inet6 ' in line:
          line= line.replace('inet6 ', '')
          line= line.lstrip();  i = line.find(' ')
          if i< 0:  self.local_ipv6= line
          else:     self.local_ipv6= line[:i]

  def get_torip(self):
    global proxy;  ipstr= myio.proxy_ip(proxy= proxy)
    if not ipstr:  ipstr= 'FETCH FAILED'
    self.vtorip.set(ipstr)

  def ping(self):            mylaunch.xterm_spawn('ping www.news.com')
  def wicd(self):            mylaunch.spawn('wicd-gtk')
  def privoxy_daemon(self):  service_restart('privoxy')
  def wicd_daemon(self):     service_restart('wicd');              self.get_misc()
  def network_daemon(self):  service_restart('network-manager');   self.get_misc()
  def tor_restart(self):     service_restart('tor');               self.get_torip()

#=======================================================================================
def service_restart(service):
  subprocess.run(['gksu', 'service', service, 'restart'])

def hostname_from_ip(ip):
  hostname= socket.gethostbyaddr(str(ip))
  return hostname[0]

 
g.domain(Fmain, packfirst= True)


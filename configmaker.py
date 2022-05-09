from configparser import ConfigParser
import guimain

class configchk:
    #Checks for the config.ini file
    def chkfile(root):
        try:  
            open('config.ini')
            guimain.nicehashapp.nxtframe(root)
        except FileNotFoundError:
            guimain.nicehashapp.credwin(root)
            
    def config_file(orgid,key,secret,rigid,chkbox,curr):
        config_object = ConfigParser()
        config_object["details"] ={
            "org_id": orgid,
            "key": key,
            "secret": secret,
            "rigid": rigid,
            "discord_rpc": chkbox,
            "currency": curr
        }
        with open('config.ini', 'w') as conf:
            config_object.write(conf)
    
    def update_config(keyname,value):
        cf_obj=ConfigParser()
        cf_obj.read('config.ini')
        cf_obj.set('details', keyname, value)
        with open('config.ini', 'w') as configfile:
            cf_obj.write(configfile)
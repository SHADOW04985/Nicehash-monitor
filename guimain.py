import tkinter as tk
from tkinter import PhotoImage, ttk, messagebox,Frame
from configparser import ConfigParser
from urllib.error import HTTPError
import APIpull
import configmaker
import requests
import gc
import os

class nicehashapp:
    def gui():
        #creating gui window
        root=tk.Tk()

        #Gui positioning
        window_width = 550
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        root.resizable(False, False)
        root.title("Nicehash Mining Status")

        root.wm_iconbitmap('logosmol.ico')

        #Nicehash Logo
        logo = PhotoImage(file = "ncbarlogo smaller.png")
        logoplace = ttk.Label( root, image = logo)
        logoplace.place(x = 187, y = 5)

        #checking for config file
        configmaker.configchk.chkfile(root)

        root.mainloop()
        
    def credwin(root):
        #Frame window to take credentials from the user
        mainwin=ttk.Frame(root)
        mainwin.pack(pady=(70,0),fill='x')

        orgid=tk.StringVar()
        key=tk.StringVar()
        secret=tk.StringVar()
        rigid=tk.StringVar()
        chkbox=tk.IntVar()
        curr=tk.StringVar()
        
        ttk.Label(mainwin, text = "Organization id:",font=(25)).grid(column=0,row=0, pady=5)
        str(ttk.Entry(mainwin, width=30,textvariable=orgid).grid(column=1, row=0, pady=5, sticky=tk.W))

        ttk.Label(mainwin, text = "Key:",font=(25)).grid(column=0,row=1, pady=5)
        str(ttk.Entry(mainwin, width=30,textvariable=key).grid(column=1, row=1, pady=5, sticky=tk.W))

        ttk.Label(mainwin, text = "Secret:",font=(25)).grid(column=0,row=2, pady=5)
        str(ttk.Entry(mainwin, width=30,textvariable=secret).grid(column=1, row=2, pady=5, sticky=tk.W))

        ttk.Label(mainwin, text = "Rigid:",font=(25)).grid(column=0,row=3, pady=5)
        str(ttk.Entry(mainwin, width=30,textvariable=rigid).grid(column=1, row=3, pady=5, sticky=tk.W))

        ttk.Label(mainwin, text = "Select your currency:",font=(25)).grid(column=0,row=5, pady=5)
        ttk.Radiobutton(mainwin,text='Dollar',value='DLR',variable=curr).grid(column=1,row=4)
        ttk.Radiobutton(mainwin,text='INR',value='RUPE',variable=curr).grid(column=1,row=5)
        ttk.Radiobutton(mainwin,text='EURO',value='EUR',variable=curr).grid(column=1,row=6)

        Submitbtn = ttk.Button(mainwin,text='Submit',
            command=lambda: [
                configmaker.configchk.config_file(orgid.get(),key.get(),secret.get(),rigid.get(),chkbox.get(),curr.get()),
                mainwin.destroy(),
                nicehashapp.nxtframe(root),
                gc.collect()  
            ])
        Submitbtn.grid(column=1,row=7, pady=5)

    #Reusable function to display error in a msgbox
    def err_pop(err,msg):
        messagebox.showinfo(err,msg)
    
    def nxtframe(root):            
        mainwin=Frame(root)
        mainwin.pack(pady=(45,0),fill='x')

        cf_obj=ConfigParser()
        cf_obj.read('config.ini')
        curr=cf_obj.get('details','currency')
        if curr=='DLR':
            sym='$'
        elif curr=='RUPE':
            sym='₹'
        else:
            sym='€'

        def destroy_widgets():
            for widgets in mainwin.winfo_children():
                widgets.destroy()
            gc.collect()
            showdata()

        def showdata():
            ttk.Label(mainwin,text = "Device Name",font=('bold',11)).grid(column=0,row=0,padx=50,pady=8)
            ttk.Label(mainwin,text = "Device Status",font=('bold',11)).grid(column=1,row=0,padx=15,pady=8)
            ttk.Label(mainwin,text = "Device Temp",font=('bold',11)).grid(column=2,row=0,padx=15,pady=8)
            ttk.Label(mainwin,text = "Hashrate",font=('bold',11)).grid(column=3,row=0,padx=15,pady=8)

            try:
                response=APIpull.pullbot.apikeys().rig_stats()
                sublst=response['devices']
                
                if response['minerStatus']=='OFFLINE' or response['minerStatus']=='STOPPED':
                    status=response['minerStatus']
                    err='Rig Status'
                    msg=f'Your Rig is in the {status} status. Start your rig and then launch the application.'
                    nicehashapp.err_pop(err,msg)
                    os._exit(1)
                
                temp=APIpull.pullbot.getTemps(sublst)

                unp=response['unpaidAmount']   
                unp=float(unp)*APIpull.pullbot.btcprice()
                unp = "{:.2f}".format(unp)

                profit = float(response["localProfitability"])
                profit*=APIpull.pullbot.btcprice()
                profit= "{:.2f}".format(profit)
                
                lstlen=len(temp)
                for i in range(1,lstlen):
                    ttk.Label(mainwin,text=sublst[i]['name'],wraplength=200).grid(column=0,row=i+1)
                    ttk.Label(mainwin,text=sublst[i]['status']['enumName']).grid(column=1,row=i+1)
                    if temp[i]==-1:
                        ttk.Label(mainwin,text='NA').grid(column=2,row=i+1)
                    else:
                        ttk.Label(mainwin,text=(temp[i],'°C')).grid(column=2,row=i+1)
                    if sublst[i]['speeds']:
                        speedlst=(sublst[i]['speeds'])
                        speed=float(speedlst[0]['speed'])
                        speed="{:.2f}".format(speed)
                        speedsym=speedlst[0]['displaySuffix']
                    else:
                        speed='NA'
                        speedsym=''
                    ttk.Label(mainwin,text=speed+speedsym).grid(column=3,row=i+1,pady=10)
                    ttk.Label(mainwin,text='Unpaid Balance: '+sym+' '+unp,font=('bold',11)).grid(column=0,row=lstlen+1,pady=10)
                    ttk.Label(mainwin,text='24Hr profit: '+profit,font=('bold',11)).grid(column=1,row=lstlen+1,pady=10)
                    ttk.Label(mainwin,text='Data Updated on: '+APIpull.pullbot.local_time()).grid(row=lstlen+2,column=1,pady=10)
                    
                    mainwin.after(60000,destroy_widgets)

            except requests.exceptions.ConnectionError:
                err='Data pull error'
                msg='Unable to connect to the internet'
                nicehashapp.err_pop(err,msg)
                os._exit(1)
            except HTTPError:
                err='Data pull error'
                msg='A temporary server error has occured click ok to retry'
                nicehashapp.err_pop(err,msg)
                mainwin.after(10000,showdata)
            except Exception as e:
                err='Unknown Error'
                msg=f"Unknown error has occured: {e}"
                nicehashapp.err_pop(err,msg)
                os._exit(1)
        mainwin.after(500,showdata)
from datetime import datetime

import infos
from JDatabase import JsonDatabase
from pyobigram.client import ObigramClient,inlineKeyboardMarkup,inlineKeyboardButton
from pyobigram.utils import get_file_size,sizeof_fmt,get_url_file_name,createID
from pydownloader.downloader import Downloader
import ProxyCloud
import pyobigram
import pydownloader
import zipfile
import ownclient

import os
import time
import config


def get_root(username):
    if os.path.isdir(config.BASE_ROOT_PATH+username)==False:
        os.mkdir(config.BASE_ROOT_PATH+username)
    return os.listdir(config.BASE_ROOT_PATH+username)

def send_root(update,bot,message,user_info,cloud=False,PROXY_OBJ=None):
    listdir = get_root(update.message.sender.username)
    reply = f'📄 Root ({len(listdir)}) 📄\n\n'
    i=-1
    if cloud:
        listdir = ownclient.getRootStacic(config.OWN_USER, config.OWN_PASSWORD,config.PROXY_OBJ)
        reply = f'📄 Root ({len(listdir)}) 📄\n\n'
        for item in listdir:
                i+=1
                fname = item
                reply += str(i) + ' - ' + fname + '\n'
        pass
    else:
        for item in listdir:
                i+=1
                fname = item
                fsize = get_file_size(config.BASE_ROOT_PATH + update.message.sender.username + '/' + item)
                prettyfsize = sizeof_fmt(fsize)
                reply += str(i) + ' - ' + fname + ' [' + prettyfsize + ']\n'
    if message:
        bot.editMessageText(message,reply)
    else:
        bot.sendMessage(update.message.chat.id, reply)

LISTENING = {}

def create_content_file(id,index,chunk):
    name = f'content-{str(index)}{id}.bin'
    respf =  open(name,'wb')
    respf.write(chunk)
    respf.close()
    return name

def get_content_name(id,index):
    return  f'content-{str(index)}{id}.bin'

def make_end(id):
    mkend = f'endcontent-{id}.txt'
    mkendf = open(mkend,'w')
    mkendf.write('END')
    mkendf.close()
    return mkend

def create_response_file(id,filename,headers):
    respname = f'resp-{id}.txt'
    respdata = f'OK\n'
    for h in headers:
        respdata+= f'{h}:{headers[h]}\n'
    respf = open(respname, 'w')
    respf.write(respdata)
    respf.close()
    return respname

def make_sync_end(id):
    mkend = f'endcontent-{id}.txt'
    mkendf = open(mkend,'w')
    mkendf.write('END')
    mkendf.close()

def progress(dl, filename, currentBits, totalBits, speed, totaltime, args,compresed=False):
    try:
        bot = args[0]
        message = args[1]

        def text_progres(index, max):
            try:
                if max < 1:
                    max += 1
                porcent = index / max
                porcent *= 100
                porcent = round(porcent)
                make_text = ''
                index_make = 1
                make_text += '\n'
                while (index_make < 21):
                    if porcent >= index_make * 5:
                        make_text += '▰'
                    else:
                        make_text += '▱'
                    index_make += 1
                make_text += ''
                return make_text
            except Exception as ex:
                return ''

        def porcent(index, max):
            porcent = index / max
            porcent *= 100
            porcent = round(porcent)
            return porcent

        if compresed:
            msg = '🧰 Comprimiendo archivo....\n'
            msg += '📁 Archivo: ' + filename + ''
            msg += '\n' + text_progres(currentBits, totalBits) + ' ' + str(porcent(currentBits, totalBits)) + '%\n' + '\n'
            msg += '☑ Total: ' + totalBits + '\n'
            msg += '🌀 Procesado: ' + currentBits + '\n'
            bot.editMessageText(message, msg)
        else:
            msg = '📡 Descargando archivo....\n'
            msg += '📁 Archivo: ' + filename + ''
            msg += '\n' + text_progres(currentBits, totalBits) + ' ' + str(porcent(currentBits, totalBits)) + '%\n' + '\n'
            msg += '☑ Total: ' + sizeof_fmt(totalBits) + '\n'
            msg += '📥 Descargado: ' + sizeof_fmt(currentBits) + '\n'
            msg += '🚀 Velocidad: ' + sizeof_fmt(speed) + '/s\n'
            msg += '⏱ Tiempo de Descarga: ' + str(time.strftime('%H:%M:%S', time.gmtime(totaltime))) + 's\n\n'
            bot.editMessageText(message, msg)

    except Exception as ex:
        print(str(ex))

def progresscompress(dl, file_name, current_bytes, total_bytes, args):
    progress(dl,file_name,current_bytes,total_bytes,0,0,args,compresed=True)

def onmessage(update,bot:ObigramClient):
    text = update.message.text
    reply_subject_text = ''
    reply_subject_file = ''

    message = None

    tl_admin_users = os.environ.get('tl_admin_user','Krixt0;obisoftt').split(';')
    username = update.message.sender.username
    jdb = JsonDatabase('database')
    jdb.check_create()
    jdb.load()

    user_info = jdb.get_user(username)
    # if username == tl_admin_user or user_info:
    if username in tl_admin_users or len(tl_admin_users)<=0:  # validate user
        if user_info is None:
            # if username == tl_admin_user:
            if username in tl_admin_users:
                jdb.create_admin(username)
            else:
                jdb.create_user(username)
            user_info = jdb.get_user(username)
            jdb.save()
    else:
        mensaje = "🚷 No tienes acceso 🚷"
        reply_markup = inlineKeyboardMarkup(
            r1=[inlineKeyboardButton('⚙Contactar Soporte⚙', url='https://t.me/legidev')]
        )
        bot.sendMessage(update.message.chat.id, mensaje, reply_markup=reply_markup)
        return

    PROXY_OBJ = ProxyCloud.parse(user_info['proxy'])

    # comandos de admin

    if '/start' in text:
        reply = '👋TGFreeFileSync👋\nEs un bot para descargar archivos gratis sincronizados'
        start_markup = inlineKeyboardMarkup(
            r1=[inlineKeyboardButton(text='🪬Github (ObisoftDev)🪬',url='https://github.com/ObisoftDev?tab=repositories'),
                inlineKeyboardButton(text='⚙️Soporte (Telegram)⚙️',url='https://t.me/obisoftt')])
        message = bot.sendMessage(update.message.chat.id,reply,parse_mode='html',reply_markup=start_markup)
        pass

    if '/ls' in text: send_root(update,bot,message,user_info,PROXY_OBJ=PROXY_OBJ)
        
    if '/rm' in text:
        index = None
        range = None
        try:
            index = int(str(text).split(' ')[1])
            range = int(str(text).split(' ')[2])
        except:
            pass
        if index != None:
            listdir = get_root(username)
            if range == None:
                rmfile = config.BASE_ROOT_PATH + username + '/' + listdir[index]
                os.unlink(rmfile)
            else:
                while index <= range:
                    rmfile = config.BASE_ROOT_PATH + username + '/' + listdir[index]
                    os.unlink(rmfile)
                    index += 1
        send_root(update,bot,message,user_info,PROXY_OBJ=PROXY_OBJ)

    if '/zip' in text:
        text = str(text).replace('/zip ','')
        index = None
        range = None
        sizemb = 99999
        try:
            index = int(str(text).split('-')[0])
            range = index+1
            try:
                range = int(str(text).split(' ')[0].split('-')[1])+1
            except:pass
            sizemb = int(str(text).split(' ')[1])
        except:
            pass
        if index != None:
            listdir = get_root(username)
            zipsplit = listdir[index].split('.')
            zipname = ''
            i=0
            for item in zipsplit:
                    if i>=len(zipsplit)-1:continue
                    zipname += item
                    i+=1
            filezise=0
            iindex = index
            while iindex<range:
                ffullpath = config.BASE_ROOT_PATH + username + '/' + listdir[index]
                filezise+=get_file_size(ffullpath)
                iindex+=1
            zipname = config.BASE_ROOT_PATH + username + '/' + zipname
            multifile = zipfile.MultiFile(zipname, 1024 * 1024 * sizemb,filezise,progressfunc=progresscompress,args=(bot,message))
            zip = zipfile.ZipFile(multifile, mode='w', compression=zipfile.ZIP_DEFLATED)
            while index<range:
                ffullpath = config.BASE_ROOT_PATH + username + '/' + listdir[index]
                message = bot.sendMessage(update.message.chat.id,f'📚Comprimiendo {listdir[index]}...')
                filezise = get_file_size(ffullpath)
                zip.write(ffullpath)
                index+=1
            zip.close()
            multifile.close()
            send_root(update,bot,message,user_info)

    if '/sync' in text:
        try:
            if LISTENING[username]:pass
        except:LISTENING[username]=True
        listenmarkup = inlineKeyboardMarkup(
            r1=[inlineKeyboardButton(text='💢Cancelar Sync💢',callback_data='/cancel '+username)])
        if LISTENING[username]==False:
            message = bot.sendMessage(update.message.chat.id,
                                     f'‼️Solo se permite una sync‼\n‼️debe cancelar la anterior‼️',
                                     reply_markup=listenmarkup)
            return
        LISTENING[username]==False
        index = 0
        range = index+1
        try:
            index = int(str(text).split(' ')[1])
            range = index+1
            range = int(str(text).split(' ')[2])+1
        except:
            pass
        if  range>=0:
            message = bot.sendMessage(update.message.chat.id, f'🧩Preparando Sync...',reply_markup=listenmarkup)
            lastfile = ''
            listdir = get_root(username)
            while index < range and LISTENING[username] == False:
                fileid = createID(12)
                filepath = config.BASE_ROOT_PATH + username + '/' + listdir[index]
                filename = listdir[index]
                readtotal = get_file_size(filepath)
                bot.editMessageText(message, f'🧩Sync For '+filename,reply_markup=listenmarkup)
               
                #resp file
                headers = {}
                headers['filename'] = filename
                headers['Content-Type'] = 'application/octet-stream'
                headers['Content-Length'] = str(readtotal)
                respf = create_response_file(fileid,filename,headers)
                ownclient.uploadstatic(config.OWN_USER, config.OWN_PASSWORD, respf, config.PROXY_OBJ)
                os.unlink(respf)

                file = open(filepath,'rb')
                chunkcounter = 0
                icontent = 1
                showsyncurl = True
                while True:

                    content = get_content_name(fileid,icontent)
                    contents = ownclient.getRootStacic(config.OWN_USER, config.OWN_PASSWORD,config.PROXY_OBJ)

                    if content not in contents:
                        chunk = file.read(config.SPLIT_SYNC)
                        content = create_content_file(fileid,icontent, chunk)
                        ownclient.uploadstatic(config.OWN_USER, config.OWN_PASSWORD, content,config.PROXY_OBJ)
                        os.unlink(content)
                        chunkcounter += len(chunk)
                        print(f'{content} Uploaded!')
                    
                    delcontent = str(content).replace('content-', f'delcontent-')
                    if delcontent in contents:
                       ownclient.deleteStacic(config.OWN_USER, config.OWN_PASSWORD, delcontent,config.PROXY_OBJ)
                       ownclient.deleteStacic(config.OWN_USER, config.OWN_PASSWORD,content,config.PROXY_OBJ)

                    if LISTENING[username] == True:break
                    icontent += 1
                    if icontent >= config.UPLOAD_SYNC: icontent = 1
                    if showsyncurl:
                        showsyncurl = False
                        sync_markup = inlineKeyboardMarkup(
                         r1=[inlineKeyboardButton(text='⬇️Enlace Sync⬇️',
                                                  url=f'http://127.0.0.1:80/download?id={fileid}')],
                         r2=[inlineKeyboardButton(text='💢Cancelar Sync💢',callback_data='/cancel '+syncid)])
                        bot.editMessageText(message, f'🧩Sync For '+filename,reply_markup=sync_markup)
                    if chunkcounter>=readtotal:break

                file.close()

                mkend = make_end(fileid)
                ownclient.uploadstatic(config.OWN_USER, config.OWN_PASSWORD, mkend, config.PROXY_OBJ)
                os.unlink(mkend)

                if LISTENING[username] == True:
                   LISTENING.pop(username)
                   icontent = 1
                   while icontent<config.UPLOAD_SYNC:
                       content = get_content_name(fileid,icontent)
                       ownclient.deleteStacic(config.OWN_USER, config.OWN_PASSWORD,content,config.PROXY_OBJ)
                       icontent+=1
                   break
                sync_markup = inlineKeyboardMarkup(
                         r1=[inlineKeyboardButton(text='⬇️Enlace Sync⬇️',
                                                  url=f'http://127.0.0.1:80/download?id={fileid}')],
                         r2=[inlineKeyboardButton(text='☑️Terminar Syn☑️',callback_data='/cancel '+syncid)])
                bot.editMessageText(message, f'☑️Sync '+filename,reply_markup=sync_markup)
                index+=1

    if 'http' in text:
        get_root(username)
        message = bot.sendMessage(update.message.chat.id, '⏳Procesando...')
        down = Downloader(config.BASE_ROOT_PATH+username+'/')
        file = down.download_url(text,progressfunc=progress,args=(bot,message))
        reply = '💚Archivo descargado💚\n'
        reply += '📄Nombre: ' + file + '\n'
        reply += '🗳Tamaño: ' + str(sizeof_fmt(get_file_size(file))) + '\n'
        bot.editMessageText(message,reply)
        send_root(update,bot,None,user_info,PROXY_OBJ=PROXY_OBJ)
        pass

    print('Finished Procesed Message!')

def cancellisten(update,bot:ObigramClient):
    try:
        cmd = str(update.data).split(' ')
        username = cmd[0]
        LISTENING[username] = True
        bot.editMessageText(update.message,'🛑Syncronizacion Cancelada🛑')
    except:pass
    pass
def delete(update,bot:ObigramClient):
    try:
        username = update.message.sender.username
        jdb = JsonDatabase('database')
        jdb.check_create()
        jdb.load()
        user_info = jdb.get_user(username)
        pathfile = str(update.data)
        PROXY_OBJ = ProxyCloud.parse(user_info['proxy'])
        ownclient.deleteStacic(config.OWN_USER, config.OWN_PASSWORD,pathfile, config.PROXY_OBJ)
        bot.editMessageText(update.message,f'🛑{pathfile} eliminado🛑')
    except Exception as ex:print(str(ex))
    pass

def main():
    print('Bot Started!')
    bot = ObigramClient(config.BOT_TOKEN)
    bot.onMessage(onmessage)
    bot.onCallbackData('/cancel ',cancellisten)
    bot.onCallbackData('/delete ',delete)
    bot.run()

if __name__ == '__main__':
    main()

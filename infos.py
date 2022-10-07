
def createStat(username,userdata,isadmin):
    msg = '⚙️Configuración de Usuario⚙️\n\n'
    msg+= '👉 Nombre: @' + str(username)+'\n'
    msg+= '👤 User: **********'
    msg+= '🔑 Password: **********'
    proxy = '✘'
    if userdata['proxy'] !='':
       proxy = '✔'
    msg+= '🔌 Proxy : ' + proxy + '\n'
    return msg

def createStat(username,userdata,isadmin):
    msg = '⚙️Configuración de Usuario⚙️\n\n'
    msg+= '👉 Nombre: @' + str(username)+'\n'
    msg+= '👤 User: ' + str(userdata['user'])+'\n'
    msg+= '🔑 Password: ' + str(userdata['password']) +'\n'
    proxy = '✘'
    if userdata['proxy'] !='':
       proxy = '✔'
    msg+= '🔌 Proxy : ' + proxy + '\n'
    return msg

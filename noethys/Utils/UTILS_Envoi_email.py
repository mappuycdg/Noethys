#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import GestionDB
import FonctionsPerso
import re
from Utils import UTILS_Html2text
from Utils import UTILS_Titulaires

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEAudio import MIMEAudio
from email.Utils import COMMASPACE, formatdate
from email.header import Header
from email.utils import formatdate, formataddr
from email import Encoders
import mimetypes





def EnvoiEmailFamille(parent=None, IDfamille=None, nomDoc="", categorie="", listeAdresses=[], visible=True, log=None, CreationPDF=None, IDmodele=None):
    # Cr�ation du PDF
    if CreationPDF != None :
        temp = CreationPDF
    else :
        temp = parent.CreationPDF
    dictChamps = temp(nomDoc=nomDoc, afficherDoc=False)
    if dictChamps == False :
        return False

    if nomDoc != False :
        liste_pieces = [nomDoc,]
    else :
        liste_pieces = []

    # Recherche adresse famille
    if len(listeAdresses) == 0 :
        listeAdresses = GetAdresseFamille(IDfamille)
        if len(listeAdresses) == 0 :
            return False
    
    # DLG Mailer
    listeDonnees = []
    for adresse in listeAdresses :
        listeDonnees.append({
            "adresse" : adresse, 
            "pieces" : liste_pieces,
            "champs" : dictChamps,
            })
    from Dlg import DLG_Mailer
    dlg = DLG_Mailer.Dialog(parent, categorie=categorie, afficher_confirmation_envoi=visible)
    dlg.SetDonnees(listeDonnees, modificationAutorisee=False)
    if IDmodele == None :
        dlg.ChargerModeleDefaut()
    else :
        dlg.ChargerModele(IDmodele)

    if visible == True :
        # Fen�tre visible
        dlg.ShowModal()

    else :
        # Fen�tre cach�e
        dlg.OnBoutonEnvoyer(None)

    if len(dlg.listeSucces) > 0 :
        resultat = True
        if log : log.EcritLog(_(u"L'Email a �t� envoy� avec succ�s."))
    else :
        resultat = False
        if log : log.EcritLog(_(u"L'email n'a pas �t� envoy�."))

    dlg.Destroy()

    # Suppression du PDF temporaire
    if nomDoc != False :
        try :
            os.remove(nomDoc)
        except :
            pass

    return resultat



def ValidationEmail(email):
    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
        return True
    else :
        return False


def GetAdresseExpDefaut():
    """ Retourne les param�tres de l'adresse d'exp�diteur par d�faut """
    return GetAdresseExp(IDadresse=None)

def GetAdresseExp(IDadresse=None):
    """ Si IDadresse = None, retourne l'adresse par d�faut"""
    if IDadresse == None :
        condition = "defaut=1"
    else :
        condition = "IDadresse=%d" % IDadresse
    # R�cup�ration des donn�es
    DB = GestionDB.DB()        
    req = """SELECT IDadresse, adresse, nom_adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS, utilisateur
    FROM adresses_mail WHERE %s ORDER BY adresse;""" % condition
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) == 0 : return None
    IDadresse, adresse, nom_adresse, motdepasse, smtp, port, defaut, auth, startTLS, utilisateur = listeDonnees[0]
    dictAdresse = {"adresse":adresse, "nom_adresse":nom_adresse, "motdepasse":motdepasse, "smtp":smtp, "port":port, "auth" : auth, "startTLS":startTLS, "utilisateur" : utilisateur}
    return dictAdresse

def GetAdresseFamille(IDfamille=None, choixMultiple=True, muet=False, nomTitulaires=None):
    """ R�cup�re l'adresse email de la famille """
    # R�cup�ration du nom de la famille
    if nomTitulaires == None :
        dictTitulaires = UTILS_Titulaires.GetTitulaires([IDfamille,])
        nomTitulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]        
    # R�cup�ration des adresses mails de chaque membre de la famille
    DB = GestionDB.DB()
    req = """
    SELECT 
    rattachements.IDindividu, IDcategorie,
    individus.nom, individus.prenom, individus.mail, individus.travail_mail
    FROM rattachements 
    LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
    WHERE IDcategorie IN (1, 2) AND IDfamille=%d
    ;""" % IDfamille
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 
    listeAdresses = []
    listeTemp = []
    for IDindividu,  IDcategorie, nom, prenom, mailPerso, mailTravail in listeDonnees :
        if mailPerso != None and mailPerso != "" and mailPerso not in listeTemp :
            listeAdresses.append((_(u"%s (Adresse perso de %s)") % (mailPerso, prenom), mailPerso))
            listeTemp.append(mailPerso)
        if mailTravail != None and mailTravail != "" and mailTravail not in listeTemp :
            listeAdresses.append((_(u"%s (Adresse pro de %s)") % (mailTravail, prenom), mailTravail))
            listeTemp.append(mailTravail)
    if len(listeAdresses) == 0 :
        if muet == False :
            dlg = wx.MessageDialog(None, _(u"Aucun membre de la famille de %s ne dispose d'adresse mail !") % nomTitulaires, "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
        return []
    elif len(listeAdresses) == 1 :
        listeMails = [listeAdresses[0][1],]
    else:
        listeLabels = []
        listeMails = []
        for label, adresse in listeAdresses :
            listeLabels.append(label)
        if choixMultiple == True :
            dlg = wx.MultiChoiceDialog(None, _(u"%d adresses internet sont disponibles pour la famille de %s.\nS�lectionnez celles que vous souhaitez utiliser puis cliquez sur le bouton 'Ok' :") % (len(listeAdresses), nomTitulaires), _(u"Choix d'adresses Emails"), listeLabels)
        else :
            dlg = wx.SingleChoiceDialog(None, _(u"%d adresses internet sont disponibles pour la famille de %s.\nS�lectionnez celle que vous souhaitez utiliser puis cliquez sur le bouton 'Ok' :") % (len(listeAdresses), nomTitulaires), _(u"Choix d'une adresse Email"), listeLabels)
        dlg.SetSize((450, -1))
        dlg.CenterOnScreen() 
        if dlg.ShowModal() == wx.ID_OK :
            if choixMultiple == True :
                selections = dlg.GetSelections()
            else :
                selections = [dlg.GetSelection(),]
            dlg.Destroy()
            if len(selections) == 0 :
                dlg = wx.MessageDialog(None, _(u"Vous n'avez s�lectionn� aucune adresse mail !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return []
            for index in selections :
                listeMails.append(listeAdresses[index][1])
        else:
            dlg.Destroy()
            return []
    
    if choixMultiple == True :
        return listeMails
    else :
        return listeMails[0]







def Envoi_mail(adresseExpediteur="", nomadresseExpediteur="", listeDestinataires=[], listeDestinatairesCCI=[], sujetMail="", texteMail="", listeFichiersJoints=[], serveur="localhost", port=None, avecAuthentification=False, avecStartTLS=False, listeImages=[], motdepasse=None, accuseReception=False, utilisateur=""):
    """ Envoi d'un mail avec pi�ce jointe """
    assert type(listeDestinataires)==list
    assert type(listeFichiersJoints)==list
    
    # Corrige le pb des images embarqu�es
    index = 0
    for img in listeImages :
        img = img.replace(u"\\", u"/")
        img = img.replace(u":", u"%3a")
        texteMail = texteMail.replace(_(u"file:/%s") % img, u"cid:image%d" % index)
        index += 1

    # Cr�ation du message
    msg = MIMEMultipart('alternative')
    #msg['Message-ID'] = make_msgid()

    if accuseReception == True :
        msg['Disposition-Notification-To'] = adresseExpediteur

    # Conversion du HTML en plain text
    textePlain = UTILS_Html2text.html2text(texteMail)

    msg.attach( MIMEText(textePlain.encode('utf-8'), 'plain', 'utf-8') )
    msg.attach( MIMEText(texteMail.encode('utf-8'), 'html', 'utf-8') )

    # on encapsule dans un Multipart en mixed suplémentaire pour palier à la mauvaise detection de la piece jointe
    # par certains lecteurs mails
    tmpmsg = msg
    msg = MIMEMultipart('mixed')
    msg.attach(tmpmsg)

    # Ajout des headers à ce Multipart
    if nomadresseExpediteur in ("", None) :
        msg['From'] = adresseExpediteur
    else:
        sender = Header(nomadresseExpediteur, "utf-8")
        sender.append(adresseExpediteur, "ascii")
        msg['From'] = sender #formataddr((nomadresseExpediteur, adresseExpediteur))
    msg['To'] = ";".join(listeDestinataires)
    msg['Bcc'] = ";".join(listeDestinatairesCCI)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = sujetMail

    # Attache des pi�ces jointes
    for fichier in listeFichiersJoints:
        """Guess the content type based on the file's extension. Encoding
        will be ignored, altough we should check for simple things like
        gzip'd or compressed files."""
        ctype, encoding = mimetypes.guess_type(fichier)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compresses), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            fp = open(fichier)
            # Note : we should handle calculating the charset
            part = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'image':
            fp = open(fichier, 'rb')
            part = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'audio':
            fp = open(fichier, 'rb')
            part = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(fichier, 'rb')
            part = MIMEBase(maintype, subtype)
            part.set_payload(fp.read())
            fp.close()
            # Encode the payload using Base64
            Encoders.encode_base64(part)
        # Set the filename parameter
        nomFichier= os.path.basename(fichier)
        if type(nomFichier) == unicode :
            nomFichier = FonctionsPerso.Supprime_accent(nomFichier)
        # changement cosmetique pour ajouter les guillements autour du filename
        part.add_header('Content-Disposition', "attachment; filename=\"%s\"" % nomFichier)
        msg.attach(part)

    # Images incluses
    index = 0
    for img in listeImages :
        fp = open(img, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<image%d>' % index)
        msgImage.add_header('Content-Disposition', 'inline', filename=img)
        msg.attach(msgImage)
        index += 1


## Certains SMTP (exemple Orange Pro) demandent une authentifcation (en g�n�ral user : boite mail et pwd : mot de passe associé au smtp sécurisé )
## mais ne supportent pas le mode starttls
## Ces identifiants sont généralement utilisés lors d'un envoi de mail abec un FAI différent du propriétaire du SMTP
## Par exemple pour envoyer un mail avec le smtp pro orange depuis un autre FAI (Free, SFR....)
##      serveur : smtp.premium.orange.fr - port 587
##      user : mon.user@orange.fr
##      pwd : mon_pwd
##  On positionne dans ce cas le parametre avecAuthentification a True
##  et le parametre avecStartTLS est positionné selon l'état du support de la fonction startTLS par le SMTP

    if motdepasse == None :
        motdepasse = ""
    if utilisateur == None :
        utilisateur = ""

    if avecAuthentification in (0, False, None) :
        # Envoi standard
        smtp = smtplib.SMTP(serveur, timeout=150)
    else:
        # Si identification SSL n�cessaire :
        smtp = smtplib.SMTP(serveur, port, timeout=150)
        smtp.ehlo()
        if avecStartTLS == True :
            smtp.starttls()
            smtp.ehlo()
        smtp.login(utilisateur.encode('utf-8'), motdepasse.encode('utf-8'))
    
    smtp.sendmail(adresseExpediteur, listeDestinataires + listeDestinatairesCCI, msg.as_string())
    smtp.close()
    
    return True



# TEST d'envoi d'emails
if __name__ == u"__main__":
    print Envoi_mail( 
        adresseExpediteur="XXX", 
        nomadresseExpediteur="My name is Bond", 
        listeDestinataires=["XXX",], 
        listeDestinatairesCCI=[], 
        sujetMail=_(u"Sujet du Mail"), 
        texteMail=_(u"Texte du Mail"), 
        listeFichiersJoints=[], 
        serveur="XXX", 
        port=465, 
        avecAuthentification=True,
        avecStartTLS=False,
        listeImages=[],
        motdepasse="XXX",
        utilisateur="XXX",
        accuseReception = False,
        )

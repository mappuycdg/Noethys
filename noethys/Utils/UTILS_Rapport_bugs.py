#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import sys
import os
import platform
import traceback
import datetime
import GestionDB
import webbrowser
import wx.lib.dialogs
import UTILS_Config
import UTILS_Customize
import UTILS_Fichiers



def Activer_rapport_erreurs(version=""):
    def my_excepthook(exctype, value, tb):
        dateDuJour = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        systeme = u"%s %s %s %s" % (sys.platform, platform.system(), platform.release(), platform.machine())
        infos = u"## %s | %s | wxPython %s | %s ##" % (dateDuJour, version, wx.version(), systeme)
        bug = ''.join(traceback.format_exception(exctype, value, tb))

        # Affichage dans le journal
        print bug

        # Affichage dans une DLG
        try :
            if UTILS_Config.GetParametre("rapports_bugs", True) == False :
                return
        except :
            pass
        try :
            texte = u"%s\n%s" % (infos, bug.decode("iso-8859-15"))
            dlg = DLG_Rapport(None, texte)
            dlg.ShowModal()
            dlg.Destroy()
        except :
            pass

    sys.excepthook = my_excepthook



# ------------------------------------------- BOITE DE DIALOGUE ----------------------------------------------------------------------------------------

class DLG_Rapport(wx.Dialog):
    def __init__(self, parent, texte=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        self.ctrl_image = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(Chemins.GetStaticPath(u"Images/48x48/Erreur.png"), wx.BITMAP_TYPE_ANY))
        self.label_ligne_1 = wx.StaticText(self, wx.ID_ANY, _(u"Noethys a rencontr� un probl�me !"))
        self.label_ligne_2 = wx.StaticText(self, wx.ID_ANY, _(u"Le rapport d'erreur ci-dessous peut servir � la r�solution de ce bug.\nMerci de bien vouloir le communiquer � l'auteur par Email ou depuis le forum."))
        self.ctrl_rapport = wx.TextCtrl(self, wx.ID_ANY, texte, style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        self.bouton_envoyer = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer � l'auteur"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_forum = CTRL_Bouton_image.CTRL(self, texte=_(u"Acc�der au forum"), cheminImage="Images/32x32/Forum.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnvoyer, self.bouton_envoyer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonForum, self.bouton_forum)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)

        # Envoi dans le presse-papiers
        clipdata = wx.TextDataObject()
        clipdata.SetText(texte)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

        self.bouton_fermer.SetFocus()


    def __set_properties(self):
        self.SetTitle(_(u"Rapport d'erreurs"))
        self.label_ligne_1.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.ctrl_rapport.SetToolTip(wx.ToolTip(_(u"Ce rapport d'erreur a �t� copi� dans le presse-papiers")))
        self.bouton_envoyer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour envoyer ce rapport d'erreur � l'auteur par Email")))
        self.bouton_forum.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ouvrir votre navigateur internet et acc�der au forum de Noethys. Vous pourrez ainsi signaler ce bug dans la rubrique d�di�e.")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((650, 450))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        grid_sizer_bas = wx.FlexGridSizer(1, 5, 10, 10)
        grid_sizer_haut = wx.FlexGridSizer(1, 2, 10, 10)
        grid_sizer_droit = wx.FlexGridSizer(3, 1, 10, 10)
        grid_sizer_haut.Add(self.ctrl_image, 0, wx.ALL, 10)
        grid_sizer_droit.Add(self.label_ligne_1, 0, 0, 0)
        grid_sizer_droit.Add(self.label_ligne_2, 0, 0, 0)
        grid_sizer_droit.Add(self.ctrl_rapport, 0, wx.EXPAND, 0)
        grid_sizer_droit.AddGrowableRow(2)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_droit, 1, wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND, 0)
        grid_sizer_bas.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_bas.Add(self.bouton_envoyer, 0, 0, 0)
        grid_sizer_bas.Add(self.bouton_forum, 0, 0, 0)
        grid_sizer_bas.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_bas.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonFermer(self, event):  
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonEnvoyer(self, event):
        # DLG Commentaires
        texteRapport = self.ctrl_rapport.GetValue()
        dlg = DLG_Envoi(self, texteRapport)
        reponse = dlg.ShowModal()
        commentaires = dlg.GetCommentaires()
        joindre_journal = dlg.GetJoindreJournal()
        dlg.Destroy()

        if reponse == wx.ID_OK :
            resultat = self.Envoi_mail(commentaires, joindre_journal)
##            if resultat == True :
##                self.EndModal(wx.ID_CANCEL)

    def OnBoutonForum(self, event):
        dlg = wx.MessageDialog(self, _(u"Noethys va ouvrir votre navigateur internet � la page du forum de Noethys. Vous n'aurez plus qu'� vous connecter avec vos identifiants Noethys et poster un nouveau message dans la rubrique d�di�e aux bugs."), _(u"Forum Noethys"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        webbrowser.open("https://www.noethys.com/index.php/forum-34/6-signaler-un-bug")

    def GetAdresseExpDefaut(self):
        """ Retourne les param�tres de l'adresse d'exp�diteur par d�faut """
        dictAdresse = {}
        # R�cup�ration des donn�es
        DB = GestionDB.DB()
        req = """SELECT IDadresse, adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS, utilisateur
        FROM adresses_mail WHERE defaut=1 ORDER BY adresse; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return None
        IDadresse, adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS, utilisateur = listeDonnees[0]
        dictAdresse = {"adresse":adresse, "motdepasse":motdepasse, "smtp":smtp, "port":port, "auth":connexionAuthentifiee, "startTLS":startTLS, "utilisateur" : utilisateur}
        return dictAdresse

    def Envoi_mail(self, commentaires="", joindre_journal=False):
        """ Envoi d'un mail avec pi�ce jointe """
        import smtplib
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEBase import MIMEBase
        from email.MIMEText import MIMEText
        from email.MIMEImage import MIMEImage
        from email.MIMEAudio import MIMEAudio
        from email.Utils import COMMASPACE, formatdate
        from email import Encoders
        import mimetypes

        IDrapport = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # texte
        texteRapport = self.ctrl_rapport.GetValue().replace("\n","<br/>")
        if len(commentaires) == 0 :
            commentaires = _(u"Aucun")
        texteMail = _(u"<u>Rapport de bug %s :</u><br/><br/>%s<br/><u>Commentaires :</u><br/><br/>%s") % (IDrapport, texteRapport, commentaires)

        # Destinataire
        listeDestinataires = ["noethys" + "@gmail.com",]

        # Exp�diteur
        dictExp = self.GetAdresseExpDefaut()
        if dictExp == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord saisir une adresse d'exp�diteur depuis le menu Param�trage > Adresses d'exp�dition d'Emails. Sinon, postez votre rapport de bug dans le forum de Noethys."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        adresseExpediteur = dictExp["adresse"]
        serveur = dictExp["smtp"]
        port = dictExp["port"]
        auth = dictExp["auth"]
        startTLS = dictExp["startTLS"]
        motdepasse = dictExp["motdepasse"]
        utilisateur = dictExp["utilisateur"]

        if adresseExpediteur == None :
            dlg = wx.MessageDialog(self, _(u"L'adresse d'exp�dition ne semble pas valide. Veuillez la v�rifier."), _(u"Envoi impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if auth == True and motdepasse == None :
            dlg = wx.MessageDialog(self, _(u"Le mot de passe associ� � l'adresse d'exp�dition ne semble pas valide. Veuillez le v�rifier."), _(u"Envoi impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if auth == True and utilisateur == None :
            dlg = wx.MessageDialog(self, _(u"Le nom d'utilisateur associ� � l'adresse d'exp�dition ne semble pas valide. Veuillez le v�rifier."), _(u"Envoi impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Cr�ation du message
        msg = MIMEMultipart()
        msg['From'] = adresseExpediteur
        msg['To'] = ";".join(listeDestinataires)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = _(u"Rapport de bug Noethys n�%s") % IDrapport

        msg.attach( MIMEText(texteMail.encode('utf-8'), 'html', 'utf-8') )

        # Attacher le journal d'erreurs
        if joindre_journal == True :
            customize = UTILS_Customize.Customize()
            nomJournal = UTILS_Fichiers.GetRepUtilisateur(customize.GetValeur("journal", "nom", "journal.log"))
            # Recherche le type
            ctype, encoding = mimetypes.guess_type(nomJournal)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            # Lecture du fichier
            fp = open(nomJournal)
            part = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
            # Header
            nomFichier = os.path.basename(nomJournal)
            part.add_header('Content-Disposition', "attachment; filename=\"%s\"" % nomFichier)
            msg.attach(part)

        # Envoi
        if auth == False :
            # Envoi standard
            smtp = smtplib.SMTP(serveur)
        else:
            # Si identification SSL n�cessaire :
            smtp = smtplib.SMTP(serveur, port, timeout=150)
            smtp.ehlo()
            if startTLS == True :
                smtp.starttls()
                smtp.ehlo()
            smtp.login(utilisateur.encode('utf-8'), motdepasse.encode('utf-8'))

        try :
            smtp.sendmail(adresseExpediteur, listeDestinataires, msg.as_string())
            smtp.close()
        except Exception, err :
            dlg = wx.MessageDialog(self, _(u"Le message n'a pas pu �tre envoy�. Merci de poster votre rapport de bug sur le forum de Noethys.\n\nErreur : %s !") % err, _(u"Envoi impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Message de confirmation
        dlg = wx.MessageDialog(self, _(u"Le rapport d'erreur a �t� envoy� avec succ�s."), _(u"Rapport envoy�"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        return True


# -------------------------------------------------------------------------------------------------------------------------------------------------------------

class DLG_Envoi(wx.Dialog):
    def __init__(self, parent, texteRapport=u""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.texteRapport = texteRapport

        self.label_ligne_1 = wx.StaticText(self, wx.ID_ANY, _(u"Le rapport est pr�t � �tre envoy�..."))
        self.label_ligne_2 = wx.StaticText(self, wx.ID_ANY, _(u"Vous pouvez ajouter ci-dessous des commentaires, remarques ou compl�ments d'informations\navant de l'envoyer � l'auteur. Il est �galement possible de joindre le rapport complet."))

        self.ctrl_commentaires = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE)

        self.check_journal = wx.CheckBox(self, -1, _(u"Joindre le journal des erreurs (Recommand�)"))

        self.bouton_apercu = CTRL_Bouton_image.CTRL(self, texte=_(u"Aper�u"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_envoyer = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer l'Email"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnvoyer, self.bouton_envoyer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Envoyer le rapport � l'auteur"))
        self.label_ligne_1.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.ctrl_commentaires.SetToolTip(wx.ToolTip(_(u"Vous pouvez saisir des commentaires ici")))
        self.check_journal.SetToolTip(wx.ToolTip(_(u"Pour faciliter la r�solution du bug, vous pouvez joindre votre rapport d'erreurs")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour visualiser le contenu du message qui sera envoy� � l'auteur")))
        self.bouton_envoyer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour envoyer le rapport et les commentaires � l'auteur")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((550, 350))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(5, 1, 10, 10)
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_base.Add(self.label_ligne_1, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        grid_sizer_base.Add(self.label_ligne_2, 0, wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base.Add(self.ctrl_commentaires, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        grid_sizer_base.Add(self.check_journal, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_envoyer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonApercu(self, event):
        """ Visualisation du message � envoyer """
        commentaires = self.ctrl_commentaires.GetValue()
        if len(commentaires) == 0 :
            commentaires = _(u"Aucun")
        message = _(u"Rapport : \n\n%s\nCommentaires : \n\n%s") % (self.texteRapport, commentaires)
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, message, _(u"Visualisation du contenu du message"))
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonEnvoyer(self, event):
        self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def GetCommentaires(self):
        return self.ctrl_commentaires.GetValue()

    def GetJoindreJournal(self):
        return self.check_journal.GetValue()


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = DLG_Rapport(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()

#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import OL_Documents_champs
import DLG_Saisie_formule
import wx.lib.agw.hyperlink as Hyperlink


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent
        
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        
    def OnLeftLink(self, event):
        dlg = DLG_Saisie_formule.Dialog(self, listeChamps=self.parent.listeChamps)
        if dlg.ShowModal() == wx.ID_OK:
            formule = dlg.GetFormule() 
            self.parent.InsertTexte(formule)
        dlg.Destroy()
        self.UpdateLink()
        

# ---------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, texte=u"", listeChamps=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent     
        self.listeChamps = listeChamps 
        self.texte = texte

        self.staticbox_texte_staticbox = wx.StaticBox(self, -1, u"Saisie de texte")
        self.staticbox_champs_staticbox = wx.StaticBox(self, -1, u"Champs disponibles")
        self.label_intro = wx.StaticText(self, -1, u"Vous pouvez �crire votre texte et ins�rer des champs en double-cliquant sur un item de la liste.", style=wx.ALIGN_CENTER)
        self.ctrl_champs = OL_Documents_champs.ListView(self, listeChamps=listeChamps, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_champs.SetMinSize((-1, 180))
        self.ctrl_champs.MAJ() 
        self.ctrl_texte = wx.TextCtrl(self, -1, self.texte, style=wx.TE_MULTILINE)
        self.hyper_formule = Hyperlien(self, label=u"Ins�rer une formule conditionnelle", infobulle=u"Cliquez ici pour ins�rer une formule conditionnelle", URL="")
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_ok, self.bouton_ok)
        
        self.ctrl_texte.SetFocus() 
        self.ctrl_texte.SetInsertionPointEnd() 

    def __set_properties(self):
        self.SetTitle(u"Saisie d'un texte")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((550, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticbox_texte = wx.StaticBoxSizer(self.staticbox_texte_staticbox, wx.VERTICAL)
        staticbox_champs = wx.StaticBoxSizer(self.staticbox_champs_staticbox, wx.VERTICAL)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        staticbox_champs.Add(self.ctrl_champs, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_champs, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        staticbox_texte.Add(self.ctrl_texte, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        staticbox_texte.Add(self.hyper_formule, 0, wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM, 5)
        grid_sizer_base.Add(staticbox_texte, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBouton_aide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("")
        
    def OnBouton_annuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBouton_ok(self, event):
        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)
    
    def GetTexte(self):
        return self.ctrl_texte.GetValue()
    
    def InsertTexte(self, texte=u""):
        positionCurseur = self.ctrl_texte.GetInsertionPoint() 
        self.ctrl_texte.WriteText(texte)
        self.ctrl_texte.SetInsertionPoint(positionCurseur+len(texte)) 
        self.ctrl_texte.SetFocus()


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    listeChamps = [
        (u"Nom de l'individu", u"DUPOND", u"{NOM_INDIVIDU}"),
        (u"Pr�nom de l'individu", u"G�rard", u"{PRENOM_INDIVIDU}"),
        ]
    dialog_1 = Dialog(None, texte=u"coucou !", listeChamps=listeChamps)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
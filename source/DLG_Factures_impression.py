#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx

import CTRL_Bandeau
import CTRL_Liste_factures
import CTRL_Factures_options
import UTILS_Facturation



class Dialog(wx.Dialog):
    def __init__(self, parent, filtres=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Bandeau
        intro = u"Cochez les factures � imprimer puis cliquez sur le bouton 'Aper�u' pour visualiser le ou les documents dans votre lecteur PDF."
        titre = u"Impression de factures"
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")
        
        # Factures
        self.box_factures_staticbox = wx.StaticBox(self, -1, u"Liste des factures")
        self.ctrl_liste_factures = CTRL_Liste_factures.CTRL(self, filtres=filtres)
        
        # Options
        self.ctrl_options = CTRL_Factures_options.CTRL(self)
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Apercu_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init Contr�les
        self.ctrl_liste_factures.MAJ() 
                

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour afficher le PDF")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((850, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
                
        # Factures
        box_factures = wx.StaticBoxSizer(self.box_factures_staticbox, wx.VERTICAL)
        box_factures.Add(self.ctrl_liste_factures, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_factures, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Options
        grid_sizer_base.Add(self.ctrl_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Imprimer")

    def OnBoutonAnnuler(self, event): 
        self.ctrl_options.MemoriserParametres() 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonApercu(self, event): 
        """ Aper�u PDF des factures """
        # Validation des donn�es saisies
        tracks = self.ctrl_liste_factures.GetTracksCoches() 
        if len(tracks) == 0 : 
            dlg = wx.MessageDialog(self, u"Vous n'avez s�lectionn� aucune facture � imprimer !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        listeIDfacture = []
        for track in tracks :
            listeIDfacture.append(track.IDfacture) 
        
        # R�cup�ration des options
        dictOptions = self.ctrl_options.GetOptions()
        if dictOptions == False :
            return False
        
##        for nom, valeur in dictOptions.iteritems() :
##            print (nom, valeur) 
            
        # Impression des factures s�lectionn�es
        facturation = UTILS_Facturation.Facturation()
        facturation.Impression(listeFactures=listeIDfacture, afficherDoc=True, dictOptions=dictOptions, repertoire=dictOptions["repertoire_copie"])
        
    





if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
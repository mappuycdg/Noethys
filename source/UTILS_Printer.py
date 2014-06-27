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
import datetime
from ObjectListView import ReportFormat
from Outils import ListCtrlPrinter
import GestionDB


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


class PreviewControlBar(wx.PyPreviewControlBar):
    def __init__(self, preview, buttons, parent):
        wx.PyPreviewControlBar.__init__(self, preview, buttons, parent)
        self.preview = preview
        self.parent = parent
        zoomDefaut = 100
        self.preview.SetZoom(zoomDefaut)
        
        # Impression
        self.staticbox_impression_staticbox = wx.StaticBox(self, -1, u"Impression")
        self.bouton_imprimer = wx.BitmapButton(self, wx.ID_PREVIEW_PRINT, wx.Bitmap("Images/32x32/Imprimante.png", wx.BITMAP_TYPE_ANY), size=(80, -1))
        
        # Impression rapide
        self.staticbox_rapide_staticbox = wx.StaticBox(self, -1, u"Impression rapide")
        self.bouton_rapide_x1 = wx.BitmapButton(self, -1, wx.Bitmap("Images/32x32/Imprimer-x1.png", wx.BITMAP_TYPE_ANY))
        self.bouton_rapide_x2 = wx.BitmapButton(self, -1, wx.Bitmap("Images/32x32/Imprimer-x2.png", wx.BITMAP_TYPE_ANY))

        # Navigation
        self.staticbox_navigation_staticbox = wx.StaticBox(self, -1, u"Navigation")
        self.bouton_premier = wx.BitmapButton(self, wx.ID_PREVIEW_FIRST, wx.Bitmap("Images/32x32/Premier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_precedent = wx.BitmapButton(self, wx.ID_PREVIEW_PREVIOUS, wx.Bitmap("Images/32x32/Precedent.png", wx.BITMAP_TYPE_ANY))
        self.bouton_suivant = wx.BitmapButton(self, wx.ID_PREVIEW_NEXT, wx.Bitmap("Images/32x32/Suivant.png", wx.BITMAP_TYPE_ANY))
        self.bouton_dernier = wx.BitmapButton(self, wx.ID_PREVIEW_LAST, wx.Bitmap("Images/32x32/Dernier.png", wx.BITMAP_TYPE_ANY))

        # Zoom
        self.staticbox_zoom_staticbox = wx.StaticBox(self, -1, u"Zoom")
        self.bouton_zoom_moins = wx.BitmapButton(self, -1, wx.Bitmap("Images/32x32/zoom_moins.png", wx.BITMAP_TYPE_ANY))
        self.ctrl_zoom = wx.Slider(self, -1, zoomDefaut, 1, 200, style=wx.SL_HORIZONTAL)
        self.ctrl_zoom.SetTickFreq(5, 1)
        self.bouton_zoom_plus = wx.BitmapButton(self, -1, wx.Bitmap("Images/32x32/zoom_plus.png", wx.BITMAP_TYPE_ANY))

        # Fermer
        self.staticbox_fermer_staticbox = wx.StaticBox(self, -1, u"Fermer")
        self.bouton_fermer = wx.BitmapButton(self, wx.ID_PREVIEW_CLOSE, wx.Bitmap("Images/32x32/Fermer.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnImpressionRapideX1, self.bouton_rapide_x1)
        self.Bind(wx.EVT_BUTTON, self.OnImpressionRapideX2, self.bouton_rapide_x2)
        self.Bind(wx.EVT_SCROLL, self.OnZoom, self.ctrl_zoom)
        self.Bind(wx.EVT_BUTTON, self.OnZoomMoins, self.bouton_zoom_moins)
        self.Bind(wx.EVT_BUTTON, self.OnZoomPlus, self.bouton_zoom_plus)

    def __set_properties(self):
        self.bouton_imprimer.SetToolTipString(u"Cliquez ici pour afficher l'impression")
        self.bouton_rapide_x1.SetToolTipString(u"Cliquez ici pour lancer une impression rapide en 1 exemplaire")
        self.bouton_rapide_x2.SetToolTipString(u"Cliquez ici pour lancer une impression rapide en 2 exemplaires")
        self.bouton_premier.SetToolTipString(u"Cliquez ici pour acc�der � la premi�re page")
        self.bouton_precedent.SetToolTipString(u"Cliquez ici pour acc�der � la page pr�c�dente")
        self.bouton_suivant.SetToolTipString(u"Cliquez ici pour acc�der � la page suivante")
        self.bouton_dernier.SetToolTipString(u"Cliquez ici pour acc�der � la derni�re page")
        self.bouton_zoom_moins.SetToolTipString(u"Cliquez ici pour faire un zoom arri�re")
        self.ctrl_zoom.SetToolTipString(u"D�placez la r�glette pour zoomer")
        self.bouton_zoom_plus.SetToolTipString(u"Cliquez ici pour faire un zoom avant")
        self.bouton_fermer.SetToolTipString(u"Cliquez ici pour fermer l'aper�u")

    def __do_layout(self):
        grid_sizer_base = wx.GridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=10, vgap=10, hgap=10)
        staticbox_fermer = wx.StaticBoxSizer(self.staticbox_fermer_staticbox, wx.VERTICAL)
        staticbox_zoom = wx.StaticBoxSizer(self.staticbox_zoom_staticbox, wx.VERTICAL)
        grid_sizer_zoom = wx.FlexGridSizer(rows=1, cols=4, vgap=0, hgap=5)
        staticbox_navigation = wx.StaticBoxSizer(self.staticbox_navigation_staticbox, wx.VERTICAL)
        grid_sizer_navigation = wx.FlexGridSizer(rows=1, cols=4, vgap=0, hgap=0)
        staticbox_rapide = wx.StaticBoxSizer(self.staticbox_rapide_staticbox, wx.VERTICAL)
        grid_sizer_rapide = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=0)
        staticbox_impression = wx.StaticBoxSizer(self.staticbox_impression_staticbox, wx.VERTICAL)
        grid_sizer_impression = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=0)
        grid_sizer_impression.Add(self.bouton_imprimer, 0, 0, 0)
        staticbox_impression.Add(grid_sizer_impression, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_commandes.Add(staticbox_impression, 1, wx.EXPAND, 0)
        grid_sizer_rapide.Add(self.bouton_rapide_x1, 0, 0, 0)
        grid_sizer_rapide.Add(self.bouton_rapide_x2, 0, 0, 0)
        staticbox_rapide.Add(grid_sizer_rapide, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_commandes.Add(staticbox_rapide, 1, wx.EXPAND, 0)
        grid_sizer_navigation.Add(self.bouton_premier, 0, 0, 0)
        grid_sizer_navigation.Add(self.bouton_precedent, 0, 0, 0)
        grid_sizer_navigation.Add(self.bouton_suivant, 0, 0, 0)
        grid_sizer_navigation.Add(self.bouton_dernier, 0, 0, 0)
        staticbox_navigation.Add(grid_sizer_navigation, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_commandes.Add(staticbox_navigation, 1, wx.EXPAND, 0)
        grid_sizer_zoom.Add(self.bouton_zoom_moins, 0, 0, 0)
        grid_sizer_zoom.Add(self.ctrl_zoom, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_zoom.Add(self.bouton_zoom_plus, 0, 0, 0)
        staticbox_zoom.Add(grid_sizer_zoom, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_commandes.Add(staticbox_zoom, 1, wx.EXPAND, 0)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        staticbox_fermer.Add(self.bouton_fermer, 0, wx.ALL, 5)
        grid_sizer_commandes.Add(staticbox_fermer, 1, wx.EXPAND, 0)
        grid_sizer_commandes.AddGrowableCol(4)
        grid_sizer_base.Add(grid_sizer_commandes, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(grid_sizer_base)
        self.Layout() 
        #grid_sizer_base.Fit(self)
    
    def OnImpressionRapideX1(self, event):
        self.ImpressionRapide(nbreExemplaires=1)
    
    def OnImpressionRapideX2(self, event):
        self.ImpressionRapide(nbreExemplaires=2)
    
    def ImpressionRapide(self, nbreExemplaires=1):
        pd = wx.PrintData()
        pd.SetPrinterName('')
        pd.SetOrientation(self.GetParent().orientation)
        pd.SetPaperId(wx.PAPER_A4)
        pd.SetQuality(wx.PRINT_QUALITY_DRAFT)
        pd.SetColour(True)
        pd.SetNoCopies(nbreExemplaires)
        pd.SetCollate(True)
        
        pdd = wx.PrintDialogData()
        pdd.SetPrintData(pd)
        
        printer = wx.Printer(pdd)
        printer.Print(self.parent, self.preview.GetPrintoutForPrinting(), False)
        
    def OnZoom(self, event): 
        zoom = self.ctrl_zoom.GetValue()
        self.preview.SetZoom(zoom)

    def OnZoomMoins(self, event):
        zoomActuel = self.ctrl_zoom.GetValue()
        zoom = zoomActuel - 10
        if zoom >= 1 :
            self.ctrl_zoom.SetValue(zoom)
            self.preview.SetZoom(zoom)

    def OnZoomPlus(self, event):
        zoomActuel = self.ctrl_zoom.GetValue()
        zoom = zoomActuel + 10
        if zoom <= 200 :
            self.ctrl_zoom.SetValue(zoom)
            self.preview.SetZoom(zoom)


        
    
class PreviewFrame(wx.PyPreviewFrame):
    def __init__(self, preview, parent, title=u"Aper�u avant impression", orientation=wx.PORTRAIT):
        wx.PyPreviewFrame.__init__(self, preview, parent, title)
        self.preview = preview
        self.orientation = orientation

        self.SetMinSize((650, 500))
        
        self.controlBar = PreviewControlBar(self.preview, wx.PREVIEW_DEFAULT, self)
        self.SetControlBar(self.controlBar)
        
        previewCanvas = wx.PreviewCanvas(self.preview, self, style=wx.SUNKEN_BORDER)
        self.SetPreviewCanvas(previewCanvas)
                
        self.SetSize((900, 700))
        self.CenterOnScreen() 

    def doClose(self, event):
         self.Close()
    
    def CreateControlBar(self):
        return PreviewControlBar(self.preview, wx.PREVIEW_DEFAULT, self)
        

class ObjectListViewPrinter():
    def __init__(self, listview, titre=u"", intro=u"", total=u"", format="A", orientation=wx.PORTRAIT):
        self.titre = titre
        self.intro = intro
        self.total = total
        self.orientation = orientation
        self.printer = ListCtrlPrinter.ListCtrlPrinter(listview, self.titre)
        self.printer.printout.margins = (wx.Point(5, 5), wx.Point(5, 5))
        self.printer.printout.printData.SetOrientation(orientation)
        self.printer.printout.printData.SetQuality(wx.PRINT_QUALITY_MEDIUM)
        dateJour = DateEngFr(str(datetime.date.today()))
        self.printer.PageFooter = (dateJour, u"%s - %s" % (self.titre, self.GetNomOrganisateur()), "%(currentPage)d / %(totalPages)d")
        ListCtrlPrinter.LISTINTRO = self.intro
        ListCtrlPrinter.LISTFOOTER = self.total
        if format == "A" : self.printer.ReportFormat = self.GetFormatA()
    
    def PreviewStandard(self):
        self.printer.PrintPreview()
    
    def Print(self):
        self.printer.Print() 
    
    def Preview(self):
        printPreview = self.printer.printout.GetPrintPreview()
##        preview_window = PreviewFrame(printPreview, None, self.titre, self.orientation)
        
        printPreview.SetZoom(100)
        frame = wx.GetApp().GetTopWindow() 
        preview_window = wx.PreviewFrame(printPreview, None, u"Aper�u avant impression")
        preview_window.Initialize()
        preview_window.MakeModal(False)
        preview_window.SetPosition(frame.GetPosition())
        preview_window.SetSize(frame.GetSize())
        preview_window.Show(True)


    def GetFormatA(self):        
        """ Param�tres du format personnalis� pour objectlistview """
        fmt = ReportFormat()
        
        headerFontName="Arial"
        rowFontName="Arial"
        
        # Ent�te de page
    ##        fmt.PageHeader.Font = wx.FFont(10, wx.FONTFAMILY_DECORATIVE, wx.FONTFLAG_BOLD, face=headerFontName)
    ##        fmt.PageHeader.TextColor = wx.WHITE
    ##        fmt.PageHeader.Background(wx.GREEN, wx.RED, space=(16, 4, 0, 4))
    ##        fmt.PageHeader.Padding = (0, 0, 0, 12)
        
        # Titre de liste
        fmt.ListHeader.Font = wx.FFont(16, wx.FONTFAMILY_DECORATIVE, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.ListHeader.TextColor = wx.BLACK
        fmt.ListHeader.Padding = (0, 12, 0, 10)
        fmt.ListHeader.TextAlignment = wx.ALIGN_LEFT
        fmt.ListHeader.Frame(wx.Pen(wx.BLACK, 0.25, wx.SOLID), space=10)
        
        # Intro
        fmt.ListIntro.Font = wx.FFont(7, wx.FONTFAMILY_DECORATIVE, face=headerFontName)
        fmt.ListIntro.Padding = (12, 2, 12, 2)
        fmt.ListIntro.TextAlignment = wx.ALIGN_LEFT
        fmt.ListIntro.CanWrap = True
        
        # Titre de colonne
        fmt.ColumnHeader.Font = wx.FFont(8, wx.FONTFAMILY_SWISS, face=headerFontName)
        fmt.ColumnHeader.Padding = (0, 15, 0, 0)
        fmt.ColumnHeader.Background(wx.Colour(200, 200, 200))
        fmt.ColumnHeader.CellPadding = 5
        fmt.ColumnHeader.TextAlignment = wx.ALIGN_CENTER
        fmt.ColumnHeader.GridPen = wx.Pen(wx.BLACK, 0.25, wx.SOLID)
        fmt.ColumnHeader.SetAlwaysCenter(True)
        
        # Titre d'un groupe
        fmt.GroupTitle.Font = wx.FFont(9, wx.FONTFAMILY_SWISS, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.GroupTitle.Padding = (2, 10, 2, 2)
        fmt.GroupTitle.CellPadding = 12
        fmt.GroupTitle.GridPen = wx.Pen(wx.BLACK, 0.25, wx.SOLID)
        
##        fmt.GroupTitle.TextColor = wx.BLUE
##        fmt.GroupTitle.Padding = (0, 12, 0, 12)
##        fmt.GroupTitle.Line(wx.BOTTOM, wx.GREEN, 4, toColor=wx.WHITE, space=0)

        # Ligne
        fmt.Row.Font = wx.FFont(8, wx.FONTFAMILY_SWISS, face=rowFontName)
        fmt.Row.CellPadding = 5
        fmt.Row.GridPen = wx.Pen(wx.BLACK, 0.25, wx.SOLID)
        fmt.Row.CanWrap = True
        
        # Pied de page
        fmt.PageFooter.Font = wx.FFont(7, wx.FONTFAMILY_DECORATIVE, face=headerFontName)
        fmt.PageFooter.Line(wx.TOP, wx.BLACK, 1, space=3)
        fmt.PageFooter.Padding = (0, 16, 0, 0)
        
        # Pied de Liste
        fmt.ListFooter.Font = wx.FFont(7, wx.FONTFAMILY_DECORATIVE, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.ListFooter.Padding = (12, 12, 0, 0)
        fmt.ListFooter.CellPadding = 5
##        fmt.ListFooter.Line(wx.TOP, wx.BLACK, 1, space=3)
        fmt.ListFooter.TextAlignment = wx.ALIGN_LEFT
        fmt.ListFooter.CanWrap = True
        
        # Divers param�tres
        fmt.IsShrinkToFit = True
        fmt.IncludeImages = True
        fmt.IsColumnHeadingsOnEachPage = True
        fmt.UseListCtrlTextFormat = True

        return fmt

    def GetNomOrganisateur(self):
        DB = GestionDB.DB()
        req = """SELECT nom, rue, cp, ville
        FROM organisateur WHERE IDorganisateur=1;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return ""
        nom = listeDonnees[0][0]
        if nom == None :
            nom = ""
        return nom


##class FramePreview(wx.Frame):
##    def __init__(self, parent, title="", printPreview=None):
##        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
##        self.parent = parent
##        self.printPreview = printPreview
##        self.previewCanvas = wx.PreviewCanvas(self.printPreview, self, style=wx.SUNKEN_BORDER)
##        self.printPreview.SetCanvas(self.previewCanvas)
##                
##        sizer_base = wx.BoxSizer(wx.VERTICAL)
##        sizer_base.Add(self.previewCanvas, 1, wx.EXPAND, 0)
##        self.SetSizer(sizer_base)
##        sizer_base.Fit(self)
##        self.Layout()



        


class FramePreview(wx.Frame):
    def __init__(self, parent, title="", printPreview=None):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.printPreview = printPreview
        
        self.panel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
        
        # Commandes
        self.bouton_premier = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/32x32/Premier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_precedent = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/32x32/Precedent.png", wx.BITMAP_TYPE_ANY))
        self.bouton_suivant = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/32x32/Suivant.png", wx.BITMAP_TYPE_ANY))
        self.bouton_dernier = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/32x32/Dernier.png", wx.BITMAP_TYPE_ANY))
        
        self.bouton_fermer = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/32x32/Fermer.png", wx.BITMAP_TYPE_ANY))
        
        self.ctrl_zoom = wx.Slider(self.panel, -1, 100, 1, 200, size=(200, -1), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        self.ctrl_zoom.SetTickFreq(5, 1)

        # Canvas preview
        self.previewCanvas = wx.PreviewCanvas(self.printPreview, self.panel, style=wx.SUNKEN_BORDER)
        self.printPreview.SetCanvas(self.previewCanvas)
        
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnPremierePage, self.bouton_premier)
        self.Bind(wx.EVT_BUTTON, self.OnPagePrecedente, self.bouton_precedent)
        self.Bind(wx.EVT_BUTTON, self.OnPageSuivante, self.bouton_suivant)
        self.Bind(wx.EVT_BUTTON, self.OnDernierePage, self.bouton_dernier)
        self.Bind(wx.EVT_BUTTON, self.OnFermer, self.bouton_fermer)
        self.Bind(wx.EVT_SCROLL, self.OnZoom, self.ctrl_zoom)
        
    def __set_properties(self):
##        _icon = wx.EmptyIcon()
##        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
##        self.SetIcon(_icon)
        self.SetMinSize((200, 200))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        # Commandes
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=10, vgap=10, hgap=10)
        grid_sizer_commandes.Add(self.bouton_premier, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_precedent, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_suivant, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_dernier, 0, 0, 0)
        grid_sizer_commandes.Add(self.ctrl_zoom, 0, 0, 0)
        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_fermer, 0, 0, 0)
        
        grid_sizer_commandes.AddGrowableCol(5)
        grid_sizer_base.Add(grid_sizer_commandes, 0, wx.EXPAND | wx.ALL, 10)
        
        # Canvas
        grid_sizer_base.Add(self.previewCanvas, 0, wx.EXPAND, 0)
        
        self.panel.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        
        # Initialisation des contr�les
        self.OnZoom(None)


    def OnPageSetup(self, event): 
        self.listCtrlPrinter.PageSetup()
        self.RefreshPreview()

    def OnPrint(self, event): 
        self.listCtrlPrinter.Print()

    def OnPremierePage(self, event): # wxGlade: MyFrame.<event_handler>
        self.printPreview.SetCurrentPage(self.printPreview.GetMinPage())

    def OnPagePrecedente(self, event): # wxGlade: MyFrame.<event_handler>
        if self.printPreview.GetCurrentPage() > self.printPreview.GetMinPage():
            self.printPreview.SetCurrentPage(self.printPreview.GetCurrentPage() - 1)

    def OnPageSuivante(self, event): # wxGlade: MyFrame.<event_handler>
        if self.printPreview.GetCurrentPage() < self.printPreview.GetMaxPage():
            self.printPreview.SetCurrentPage(self.printPreview.GetCurrentPage() + 1)

    def OnDernierePage(self, event): # wxGlade: MyFrame.<event_handler>
        self.printPreview.SetCurrentPage(self.printPreview.GetMaxPage())

    def OnZoom(self, event): 
        zoom = self.ctrl_zoom.GetValue()
        self.printPreview.SetZoom(zoom)

    def RefreshPreview(self):
        self.printPreview.RenderPage(min(self.printPreview.GetCurrentPage(), self.printPreview.GetMaxPage()))
        self.previewCanvas.Refresh()
    
    def OnFermer(self, event):
        self.Destroy() 


#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import datetime
import GestionDB
import CTRL_Saisie_heure
import wx.combo

COULEUR_FOND_REGROUPEMENT = (200, 200, 200)
COULEUR_TEXTE_REGROUPEMENT = (140, 140, 140)



class Track(object):
    def __init__(self, donnees):
        self.IDunite = donnees[0]
        self.IDactivite = donnees[1]
        self.nomUnite = donnees[2]
        self.typeUnite = donnees[3]
        self.nomActivite = donnees[4]
        self.coeffUnite = None

        # Items HyperTreeList
        self.item = None
        self.itemParent = None
        
        # Contr�les
        self.ctrl_type = None
        self.ctrl_coeff  = None
        self.ctrl_arrondi  = None
        self.ctrl_duree_seuil  = None
        self.ctrl_duree_plafond  = None
        self.ctrl_heure_seuil  = None
        self.ctrl_heure_plafond  = None
        self.ctrl_formule = None

    def GetType(self):
        """ Retourne le type de calcul s�lectionn� """
        return self.ctrl_type.GetSelection() 
    
    def ValidationCoeff(self):
        return self.ctrl_coeff.Validation()
    
    def GetCoeff(self):
        return self.ctrl_coeff.GetValeur() 

    def GetCoeffStr(self):
        return self.ctrl_coeff.GetValeurStr() 

    def SetCoeff(self, valeur=None):
        self.ctrl_coeff.SetValeur(valeur)
    
    def GetArrondi(self):
        return self.ctrl_arrondi.GetValeur() 

    def GetDureePlafond(self):
        if self.ctrl_duree_plafond.GetHeure() != None and self.ctrl_duree_plafond.Validation() == False :
            return False
        return self.ctrl_duree_plafond.GetValeur()

    def GetDureeSeuil(self):
        if self.ctrl_duree_seuil.GetHeure() != None and self.ctrl_duree_seuil.Validation() == False :
            return False
        return self.ctrl_duree_seuil.GetValeur()

    def GetHeurePlafond(self):
        if self.ctrl_heure_plafond.GetHeure() != None and self.ctrl_heure_plafond.Validation() == False :
            return False
        return self.ctrl_heure_plafond.GetValeur()

    def GetHeureSeuil(self):
        if self.ctrl_heure_seuil.GetHeure() != None and self.ctrl_heure_seuil.Validation() == False :
            return False
        return self.ctrl_heure_seuil.GetValeur()

    def GetFormule(self):
        return self.ctrl_formule.GetValue()

    def GetParametres(self):
        dictParametres = {
            "IDunite": self.IDunite,
            "typeCalcul": self.ctrl_type.GetParametre(),
            "coeff": self.GetCoeff(),
            "arrondi": self.ctrl_arrondi.GetParametre(),
            "duree_plafond": self.GetDureePlafond(),
            "duree_seuil": self.GetDureeSeuil(),
            "heure_plafond": self.GetHeurePlafond(),
            "heure_seuil": self.GetHeureSeuil(),
            "formule": self.GetFormule(),
            }
        return dictParametres

    def SetParametres(self, dictParametres={}):
        # Coeff
        if dictParametres.has_key("coeff") :
            self.ctrl_coeff.SetValeur(dictParametres["coeff"])
        # Arrondi
        if dictParametres.has_key("arrondi") :
            self.ctrl_arrondi.SetParametre(dictParametres["arrondi"])
        # Type de calcul
        if dictParametres.has_key("typeCalcul") :
            self.ctrl_type.SetParametre(dictParametres["typeCalcul"])
        # Dur�e seuil
        if dictParametres.has_key("duree_seuil") :
            self.ctrl_duree_seuil.SetValeur(dictParametres["duree_seuil"])
        # Dur�e plafond
        if dictParametres.has_key("duree_plafond") :
            self.ctrl_duree_plafond.SetValeur(dictParametres["duree_plafond"])
        # Heure seuil
        if dictParametres.has_key("heure_seuil") :
            self.ctrl_heure_seuil.SetValeur(dictParametres["heure_seuil"])
        # Heure plafond
        if dictParametres.has_key("heure_plafond") :
            self.ctrl_heure_plafond.SetValeur(dictParametres["heure_plafond"])
        # Formule
        if dictParametres.has_key("formule") :
            self.ctrl_formule.SetValue(dictParametres["formule"])

# --------------------------------------------------------------------------------------------------------------------------------

class CTRL_Type(wx.Choice):
    def __init__(self, parent, id=-1, item=None, track=None):
        """ Type de calcul : Par unit� ou par avec coefficient """
        wx.Choice.__init__(self, parent, id=id, size=(200, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
        self.SetItems([_(u"Nombre d'unit�s consomm�es"), _(u"Temps r��l de pr�sence"), _(u"Temps de pr�sence factur�"), _(u"Formule")])
        self.SetToolTip(wx.ToolTip(_(u"S�lectionnez le type de calcul � appliquer � cette unit� de consommation")))
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        # Defaut
        if self.track.typeUnite == "Horaire" :
            self.SetSelection(1)
        else:
            self.SetSelection(0)

    def OnChoice(self, event=None):
        self.track.ctrl_coeff.Enable(self.GetSelection() == 0)
        self.track.ctrl_arrondi.Enable(self.GetSelection() == 1)
        self.track.ctrl_duree_seuil.Enable(self.GetSelection() == 1)
        self.track.ctrl_duree_plafond.Enable(self.GetSelection() == 1)
        self.track.ctrl_heure_seuil.Enable(self.GetSelection() == 1)
        self.track.ctrl_heure_plafond.Enable(self.GetSelection() == 1)
        self.track.ctrl_formule.Enable(self.GetSelection() == 3)

    def SetParametre(self, index=0):
        self.SetSelection(index)
        self.OnChoice()

    def GetParametre(self):
        return self.GetSelection()



# -------------------------------------------------------------------------------------------------------------------

class CTRL_Arrondi(wx.Choice):
    def __init__(self, parent, id=-1, item=None, track=None):
        """ Arrondi � appliquer. Ex : Au quart d'heures sup�rieur """
        wx.Choice.__init__(self, parent, id=id, size=(140, -1))
        self.parent = parent
        self.item = item
        self.track = track

        self.listeValeurs = [
            (_(u"Aucun"), None),
            (_(u"Dur�e : 5 min. sup."), ("duree", 5)),
            (_(u"Dur�e : 10 min. sup."), ("duree", 10)),
            (_(u"Dur�e : 15 min. sup."), ("duree", 15)),
            (_(u"Dur�e : 30 min. sup."), ("duree", 30)),
            (_(u"Dur�e : 60 min. sup."), ("duree", 60)),
            (_(u"Horaire : 5 min."), ("tranche_horaire", 5)),
            (_(u"Horaire : 10 min."), ("tranche_horaire", 10)),
            (_(u"Horaire : 15 min."), ("tranche_horaire", 15)),
            (_(u"Horaire : 30 min."), ("tranche_horaire", 30)),
            (_(u"Horaire : 60 min."), ("tranche_horaire", 60)),
            ]

        self.listeLabels = []
        self.listeArrondis = []
        for label, valeur in self.listeValeurs :
            self.listeLabels.append(label)
            self.listeArrondis.append(valeur)

        self.SetItems(self.listeLabels)
        self.SetToolTip(wx.ToolTip(_(u"S�lectionnez un arrondi � appliquer � chaque consommation. \n\nExemples : \n\nDur�e 15 min. sup. = Arrondit la dur�e de la consommation aux 15 minutes sup�rieures (Si dur�e = 1h20 alors la dur�e devient 1h30)\n\nHoraire 30 min. = Arrondit l'heure de d�but � la demi-heure inf�rieure et l'heure de fin � la demi-heure sup�rieure (Si consommation de 13h10 � 13h45 alors dur�e = 1h)")))
        # Defaut
        self.SetSelection(0)
    
    def GetValeur(self):
        index = self.GetSelection() 
        return self.listeArrondis[index]

    def SetParametre(self, index=0):
        self.SetSelection(index)

    def GetParametre(self):
        return self.GetSelection()

# -------------------------------------------------------------------------------------------------------------------

class CTRL_Coeff(wx.TextCtrl):
    def __init__(self, parent, id=-1, item=None, track=None):
        """ Coefficient � appliquer"""
        wx.TextCtrl.__init__(self, parent, id=id, value="", size=(70, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
        self.SetToolTip(wx.ToolTip(_(u"Saisissez le coefficient multiplicateur � appliquer")))
    
    def Validation(self):
        valeur = self.GetValue() 
        if valeur == "" : return True
        try :
            test = float(valeur)
        except :
            return False
        return True
    
    def GetValeurStr(self):
        return self.GetValue() 
        
    def GetValeur(self):
        valeur = self.GetValue() 
        if self.Validation() == True :
            if valeur == "" : 
                return 0
            else:
                return float(valeur)
        else:
            return None
    
    def SetValeur(self, valeur=None):
        if valeur in (None, 0, 0.0) : 
            valeur = ""
        try :
            self.SetValue(str(valeur))
        except :
            pass
                    
# -------------------------------------------------------------------------------------------------------------------

class CTRL_Heure(CTRL_Saisie_heure.Heure):
    def __init__(self, parent, id=-1, item=None, track=None, tooltip=""):
        CTRL_Saisie_heure.Heure.__init__(self, parent)
        self.parent = parent
        self.SetSize((80, -1))
        self.item = item
        self.track = track
        self.SetToolTip(wx.ToolTip(tooltip))
    
    def GetValeur(self):
        valeur = self.GetHeure() 
        if self.Validation() == True :
            return valeur
        else:
            return None

    def SetValeur(self, heure=None):
        self.SetHeure(heure)


# -------------------------------------------------------------------------------------------------------------------

class CTRL_Formule(wx.combo.ComboCtrl):
    def __init__(self, *args, **kw):
        wx.combo.ComboCtrl.__init__(self, *args, **kw)

        # make a custom bitmap showing "..."
        bw, bh = 14, 16
        bmp = wx.EmptyBitmap(bw, bh)
        dc = wx.MemoryDC(bmp)
        bgcolor = wx.Colour(255, 254, 255)
        dc.SetBackground(wx.Brush(bgcolor))
        dc.Clear()
        dc.DrawBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY), 0, 0)
        del dc

        # now apply a mask using the bgcolor
        bmp.SetMaskColour(bgcolor)

        # and tell the ComboCtrl to use it
        self.SetButtonBitmaps(bmp, True)

    # Overridden from ComboCtrl, called when the combo button is clicked
    def OnButtonClick(self):
        dlg = DLG_Saisie_formule(self, texte=self.GetValue())
        if dlg.ShowModal() == wx.ID_OK :
            self.SetValue(dlg.GetTexte())
        dlg.Destroy()
        self.SetFocus()

    # Overridden from ComboCtrl to avoid assert since there is no ComboPopup
    def DoSetPopupControl(self, popup):
        pass

    def Enable(self, etat=True):
        self.GetTextCtrl().Enable(etat)


class DLG_Saisie_formule(wx.Dialog):
    def __init__(self, parent, texte=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        if texte == None :
            texte = ""

        # Texte
        self.staticbox_texte_staticbox = wx.StaticBox(self, -1, _(u"Formule python"))
        self.ctrl_texte = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE )
        self.ctrl_texte.SetMinSize((600, 250))

        formule_exemple = u"""Exemples de variables et de fonctions sp�ciales :
        debut, fin, duree, HEURE(), SI(condition, alors, sinon), ET, OU
        
Exemple de formule :
        SI(debut <= HEURE("9h") ET fin >= HEURE("7h00"), HEURE("2h"))
        + SI(debut <= HEURE("12h") ET fin >= HEURE("9h00"), HEURE("3h"))
        + SI(debut <= HEURE("14h") ET fin >= HEURE("12h00"), HEURE("2h00"))"""
        self.ctrl_exemple = wx.StaticText(self, -1, formule_exemple)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_supprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Effacer"), cheminImage="Images/32x32/Gomme.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Init
        self.ctrl_texte.SetValue(texte)
        self.ctrl_texte.SetFocus()

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une formule"))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour acc�der � l'aide")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour effacer le contenu du texte")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider ou tapez sur la touche Entr�e du clavier")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        # Texte
        staticbox_texte = wx.StaticBoxSizer(self.staticbox_texte_staticbox, wx.VERTICAL)
        staticbox_texte.Add(self.ctrl_texte, 1, wx.ALL|wx.EXPAND, 5)
        staticbox_texte.Add(self.ctrl_exemple, 0, wx.ALL | wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_texte, 1, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Etatglobal")

    def OnBoutonSupprimer(self, event=None):
        self.ctrl_texte.SetValue("")
        self.EndModal(wx.ID_OK)

    def OnBoutonOk(self, event=None):
        self.EndModal(wx.ID_OK)

    def GetTexte(self):
        texte = self.ctrl_texte.GetValue()
        texte = texte.strip()
        if texte.endswith("\n"):
            texte = texte[:-1]
        return texte


# -------------------------------------------------------------------------------------------------------------------

class CTRL(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent

        self.dict_parametres = {}
        self.listeTracks = []
        self.listeActivites = []
        self.periode = (None, None)
                
        # Cr�ation des colonnes
        listeColonnes = [
            ( _(u"Unit� de consommation"), 225, wx.ALIGN_LEFT),
            ( _(u"Type de calcul"), 210, wx.ALIGN_LEFT),
            ( _(u"Coefficient"), 80, wx.ALIGN_LEFT),
            ( _(u"Formule"), 100, wx.ALIGN_LEFT),
            ( _(u"Arrondi"), 150, wx.ALIGN_LEFT),
            ( _(u"Dur�e seuil"), 90, wx.ALIGN_LEFT),
            ( _(u"Dur�e plafond"), 90, wx.ALIGN_LEFT),
            ( _(u"Heure seuil"), 90, wx.ALIGN_LEFT),
            ( _(u"Heure plafond"), 90, wx.ALIGN_LEFT),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
        
        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_ROW_LINES |  TR_COLUMN_LINES |wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)
                    
    def Importation(self):
        # V�rifie les dates de la p�riode
        date_debut, date_fin = self.periode
        if date_debut == None or date_fin == None :
            return []
        
        # Importation des unit�s de consommations
        if len(self.listeActivites) == 0 : return []
        elif len(self.listeActivites) == 1 : conditionActivites = "unites.IDactivite=%d" % self.listeActivites[0]
        else : conditionActivites = "unites.IDactivite IN %s" % str(tuple(self.listeActivites))
        DB = GestionDB.DB()
        req = """SELECT 
        unites.IDunite, unites.IDactivite, unites.nom, unites.type,
        activites.nom
        FROM unites
        LEFT JOIN activites ON activites.IDactivite = unites.IDactivite
        WHERE %s
        AND (activites.date_debut<='%s' AND activites.date_fin>='%s')
        ORDER BY ordre
        ;""" % (conditionActivites, date_fin, date_debut)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        listeTracks = []
        for item in listeDonnees :
            track = Track(item)
            listeTracks.append(track)

        return listeTracks

    def MAJ(self, reinitialisation=False):
        """ Met � jour (redessine) tout le contr�le """
        # M�morise les param�tres de chaque unit�
        dict_parametres = self.GetParametres()
        if len(dict_parametres) > 0 :
            self.dict_parametres = dict_parametres
        if reinitialisation :
            self.dict_parametres = {}
        # MAJ du Ctrl
        self.Freeze()
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        # Applique les parametres m�moris�s
        self.SetParametres(self.dict_parametres)
        self.Thaw()

    def Remplissage(self):        
        # Importation des donn�es
        listeTracks = self.Importation() 

        # Regroupement
        listeKeys = []
        for track in listeTracks :
            key = (track.nomActivite, track.IDactivite)
            if key not in listeKeys :
                listeKeys.append(key)
                    
        # Tri des Keys
        listeKeys.sort()
        
        # Cr�ation des branches
        for nomActivite, IDactivite in listeKeys :
            
            # Niveau Nom de l'activit�
            brancheActivite = self.AppendItem(self.root, nomActivite)
            self.SetPyData(brancheActivite, IDactivite)
            self.SetItemBold(brancheActivite, True)
            self.SetItemBackgroundColour(brancheActivite, wx.Colour(*COULEUR_FOND_REGROUPEMENT))
            
            # Niveau Unit�s de consommation
            for track in listeTracks :
                
                if track.IDactivite == IDactivite :
                
                    brancheUnite = self.AppendItem(brancheActivite, track.nomUnite, ct_type=1)
                    self.SetPyData(brancheUnite, track.IDunite)
                    self.CheckItem(brancheUnite, True)
                    
                    # M�morisation des items dans le track
                    track.item = brancheUnite
                    track.itemParent = brancheActivite
                                        
                    # CTRL du type de calcul
                    ctrl_type = CTRL_Type(self.GetMainWindow(), item=brancheUnite, track=track)
                    self.SetItemWindow(brancheUnite, ctrl_type, 1)        
                    track.ctrl_type = ctrl_type      
                                        
                    # CTRL du Coeff
                    ctrl_coeff = CTRL_Coeff(self.GetMainWindow(), item=brancheUnite, track=track)
                    self.SetItemWindow(brancheUnite, ctrl_coeff, 2)        
                    track.ctrl_coeff = ctrl_coeff

                    # CTRL de la formule
                    ctrl_formule = CTRL_Formule(self.GetMainWindow(), size=(94, -1))
                    self.SetItemWindow(brancheUnite, ctrl_formule, 3)
                    track.ctrl_formule = ctrl_formule

                    # CTRL de l'Arrondi
                    ctrl_arrondi = CTRL_Arrondi(self.GetMainWindow(), item=brancheUnite, track=track)
                    self.SetItemWindow(brancheUnite, ctrl_arrondi, 4)
                    track.ctrl_arrondi = ctrl_arrondi

                    # CTRL dur�e seuil
                    ctrl_duree_seuil = CTRL_Heure(self.GetMainWindow(), item=brancheUnite, track=track, tooltip=_(u"Saisissez la dur�e seuil pour chaque consommation : La dur�e de chaque consommation ne pourra �tre inf�rieure � cette valeur"))
                    self.SetItemWindow(brancheUnite, ctrl_duree_seuil, 5)
                    track.ctrl_duree_seuil = ctrl_duree_seuil

                    # CTRL dur�e plafond
                    ctrl_duree_plafond = CTRL_Heure(self.GetMainWindow(), item=brancheUnite, track=track, tooltip=_(u"Saisissez la dur�e plafond pour chaque consommation : La dur�e de chaque consommation ne pourra �tre sup�rieure � cette valeur"))
                    self.SetItemWindow(brancheUnite, ctrl_duree_plafond, 6)
                    track.ctrl_duree_plafond = ctrl_duree_plafond

                    # CTRL heure seuil
                    ctrl_heure_seuil = CTRL_Heure(self.GetMainWindow(), item=brancheUnite, track=track, tooltip=_(u"Saisissez une heure seuil pour chaque consommation : La dur�e sera calcul�e uniquement � partir de cette heure-l�"))
                    self.SetItemWindow(brancheUnite, ctrl_heure_seuil, 7)
                    track.ctrl_heure_seuil = ctrl_heure_seuil

                    # CTRL heure plafond
                    ctrl_heure_plafond = CTRL_Heure(self.GetMainWindow(), item=brancheUnite, track=track, tooltip=_(u"Saisissez une heure plafond pour chaque consommation : La dur�e sera calcul�e uniquement jusqu'� cette heure-l�"))
                    self.SetItemWindow(brancheUnite, ctrl_heure_plafond, 8)
                    track.ctrl_heure_plafond = ctrl_heure_plafond

                    ctrl_type.OnChoice()

        self.ExpandAllChildren(self.root)
        
        # Pour �viter le bus de positionnement des contr�les
        self.GetMainWindow().CalculatePositions() 
        
        self.listeTracks = listeTracks
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()
    
    def GetDictCoeff(self):
        # M�morise les coeff d�j� saisis
        for track in self.listeTracks :
            if self.IsItemChecked(track.item) :
                if track.GetType() == 0 :
                    if track.ValidationCoeff() == True :
                        self.dictCoeff[track.IDunite] = track.GetCoeffStr()
        return self.dictCoeff
    
    def GetDonnees(self):
        """ R�cup�re les r�sultats des donn�es saisies """
        dictDonnees = {}
        for track in self.listeTracks :
            
            if self.IsItemChecked(track.item) :
                coeff = None
                arrondi = None
                duree_plafond = None
                duree_seuil = None
                heure_plafond = None
                heure_seuil = None
                formule = None

                typeCalcul = track.GetType()
                if typeCalcul == 0 :
                    # Heure selon coeff
                    if track.ValidationCoeff() == False :
                        dlg = wx.MessageDialog(self, _(u"Le coefficient de l'unit� '%s' semble incorrecte !") % track.nomUnite, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return False
                    coeff = track.GetCoeff() 

                elif typeCalcul == 1 :
                    # heures r�elles
                    if track.GetDureeSeuil() == False :
                        dlg = wx.MessageDialog(self, _(u"Le seuil de l'unit� '%s' semble incorrecte !") % track.nomUnite, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return False

                    if track.GetDureePlafond() == False :
                        dlg = wx.MessageDialog(self, _(u"Le plafond de l'unit� '%s' semble incorrecte !") % track.nomUnite, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return False

                    if track.GetHeureSeuil() == False :
                        dlg = wx.MessageDialog(self, _(u"L'heure seuil de l'unit� '%s' semble incorrecte !") % track.nomUnite, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return False

                    if track.GetHeurePlafond() == False :
                        dlg = wx.MessageDialog(self, _(u"L'heure plafond de l'unit� '%s' semble incorrecte !") % track.nomUnite, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return False

                    if track.GetHeurePlafond() != None and track.GetHeureSeuil() != None and track.GetHeurePlafond() < track.GetHeureSeuil() :
                        dlg = wx.MessageDialog(self, _(u"L'heure plafond de l'unit� '%s' doit obligatoirement �tre sup�rieure � l'heure seuil !") % track.nomUnite, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return False

                    arrondi = track.GetArrondi()
                    duree_seuil = track.GetDureeSeuil()
                    duree_plafond = track.GetDureePlafond()
                    heure_seuil = track.GetHeureSeuil()
                    heure_plafond = track.GetHeurePlafond()

                elif typeCalcul == 2:
                    # Heures factur�es
                    pass

                elif typeCalcul == 3:
                    formule = track.GetFormule()


                # M�morisation des valeurs
                dictValeurs = {
                    "IDunite" : track.IDunite,
                    "IDactivite" : track.IDactivite,
                    "nomUnite" : track.nomUnite,
                    "nomActivite" : track.nomActivite,
                    "typeCalcul" : typeCalcul,
                    "coeff" : coeff,
                    "arrondi" : arrondi,
                    "duree_plafond" : duree_plafond,
                    "duree_seuil" : duree_seuil,
                    "heure_plafond" : heure_plafond,
                    "heure_seuil" : heure_seuil,
                    "formule": formule,
                    }
                dictDonnees[track.IDunite] = dictValeurs
        
        return dictDonnees
                

    def GetParametres(self):
        """ R�cup�ration des param�tres pour sauvegarde dans profil """
        dictParametres = {}
        for track in self.listeTracks:
            dictParametres["parametres_unite_%d" % track.IDunite] = track.GetParametres()
        return dictParametres

    def SetParametres(self, dictParametres={}):
        """ Importation de param�tres """
        # R�initialisation si aucun profil
        if dictParametres == None :
            self.MAJ(reinitialisation=True)
            return
        # Envoi des param�tres au Ctrl
        for IDunite, dictParametresTrack in dictParametres.iteritems():
            if type(IDunite) in (str, unicode) and IDunite.startswith("parametres_unite_"):
                IDunite = int(IDunite.replace("parametres_unite_", ""))
            for track in self.listeTracks:
                if IDunite == track.IDunite :
                    track.SetParametres(dictParametresTrack)

        # M�morisation des param�tres
        self.dict_parametres = dictParametres

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        self.ctrl = CTRL(panel)
        self.ctrl.periode = (datetime.date(2016, 1, 1), datetime.date(2016, 12, 31))
        self.ctrl.listeActivites = [1,]
        self.ctrl.MAJ()

        self.boutonTest = wx.Button(panel, -1, _(u"Test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
    
    def OnBoutonTest(self, event):
        print self.ctrl.GetParametres()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()

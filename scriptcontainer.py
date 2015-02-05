import os
import sys

import xml.etree.ElementTree as xml
from cStringIO import StringIO

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import pysideuic
import shiboken

import json

import maya.OpenMayaUI
import maya.cmds as mc

def get_pyside_class(ui_file):
   """
   Pablo Winant
   """
   parsed = xml.parse( ui_file )
   widget_class = parsed.find( 'widget' ).get( 'class' )
   form_class = parsed.find( 'class' ).text

   with open( ui_file, 'r' ) as f:
      o = StringIO()
      frame = {}

      pysideuic.compileUi( f, o, indent = 0 )
      pyc = compile( o.getvalue(), '<string>', 'exec' )
      exec pyc in frame

      # Fetch the base_class and form class based on their type in the xml from designer
      form_class = frame['Ui_{0}'.format( form_class )]
      base_class = eval( 'QtGui.{0}'.format( widget_class ) )

   return form_class, base_class
def wrapinstance( ptr, base = None ):
   """
   Nathan Horne
   """
   if ptr is None:
      return None

   ptr = long( ptr ) #Ensure type
   if globals().has_key( 'shiboken' ):
      if base is None:
         qObj = shiboken.wrapInstance( long( ptr ), QtCore.QObject )
         metaObj = qObj.metaObject()
         cls = metaObj.className()
         superCls = metaObj.superClass().className()
         if hasattr( QtGui, cls ):
            base = getattr( QtGui, cls )

         elif hasattr( QtGui, superCls ):
            base = getattr( QtGui, superCls )

         else:
            base = QtGui.QWidget

      return shiboken.wrapInstance( long( ptr ), base )

   elif globals().has_key( 'sip' ):
      base = QtCore.QObject

      return sip.wrapinstance( long( ptr ), base )

   else:
      return None
def get_maya_window():
   maya_window_util = maya.OpenMayaUI.MQtUtil.mainWindow()
   maya_window = wrapinstance( long( maya_window_util ), QtGui.QWidget )

   return maya_window

WINDOW_TITLE = "Script Container"
WINDOW_VERSION = "Alpha 01"
WINDOW_NAME = "scriptcontainer_window"

TOOLPATH = os.path.dirname(__file__)
UI_FILE = os.path.join(TOOLPATH, "scriptcontainerUI.ui")
DATAFILEPATH = os.path.join(TOOLPATH, "scriptcontainerDATA")
UI_OBJECT, BASE_CLASS = get_pyside_class(UI_FILE)

class ScriptContainer( BASE_CLASS, UI_OBJECT ):
    def __init__(self, parent = get_maya_window(), *args):
        super(ScriptContainer, self).__init__(parent)
        self.setupUi(self)  # inherited

        self.setWindowTitle ("{0} - {1}".format(WINDOW_TITLE, str(WINDOW_VERSION)))
        #self.BUTTONNAME.clicked.connect ( self.METHODNAME )  # verbind de functies zo!!!
        self.btn_savescript.clicked.connect(self.save_script)
        self.btn_deletescript.clicked.connect(self.delete_script)
        self.btn_runscript.clicked.connect(self.run_script)

        self.listwidget.itemSelectionChanged.connect(self.updated_selection)
        #self.btn_editscript.clicked.connect(self.edit_script)
        #self.btn_deletescript.clicked.connect(self.delete_script)

        #self.METHOD_METEEN_UITVOEREN()  # Voorbeeld!!
        self.savedscripts = self.get_script_data()
        self.update_listwidget(self.savedscripts)
        self.show()

    #  Functies toevoegen doe je zo.
    #def METHODNAME(self):
    #    foo = "bar"
    #    return foo

    def get_script_data(self):
        if not os.path.isfile(DATAFILEPATH):
            data = open(DATAFILEPATH, "w")
            data.close()
            savedscripts = {}
        else:
            data = open(DATAFILEPATH)
            savedscripts = json.load(data)
        return savedscripts

    def update_listwidget(self, savedscripts):
        self.listwidget.clear()
        for k in savedscripts:
            item = QtGui.QListWidgetItem("{0}".format(k))
            self.listwidget.addItem(item)

    def updated_selection(self):
        if self.listwidget.selectedItems():
            scriptname = self.listwidget.currentItem().text()
            scriptcontent = self.savedscripts[scriptname]
            self.input_scriptname.setText(scriptname)
            self.input_script.setPlainText(scriptcontent)

    def run_script(self):
        if self.listwidget.selectedItems():
            scriptname = self.listwidget.currentItem().text()
            exec self.savedscripts[scriptname]

    def save_script(self):
        self.savedscripts.update({str(self.input_scriptname.text()):str(self.input_script.toPlainText())})
        self.write_data(self.savedscripts)
        self.update_listwidget(self.savedscripts)
        #print "save script"

    def delete_script(self):
        del self.savedscripts[self.listwidget.currentItem().text()]
        self.write_data(self.savedscripts)
        self.update_listwidget(self.savedscripts)
        self.input_scriptname.setText("")
        self.input_script.setPlainText("")
        #print "delete script"

    def write_data(self, savedscripts):
        savedscriptsJSON = json.dumps(savedscripts)
        datafile = open(DATAFILEPATH, "w")
        datafile.write(savedscriptsJSON)
        datafile.close()
        #print "writing. . ."


def show_ui():
    if mc.window(WINDOW_NAME, exists = True, q = True):
        mc.deleteUI(WINDOW_NAME)

    ScriptContainer()  # Instance je tool-class


##  NEEDED SCRIPTS TO RUN PYSIDE Qt in Maya!



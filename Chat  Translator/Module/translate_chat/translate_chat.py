from typing import Text
from base import module
from base.module import ModuleBase, ModuleAdminCommand
from base.events import EVT_CHATMESSAGE
from  googletrans import Translator
#import re
import langid
class  ChatTranslateModule(ModuleBase):
    module_name  = "Chat_Translate"
    def setup(self):
        #DetectorFactory.seed  =  0
        self._module_data  = self.get_module_data()
        self.langs  =  ("af", "ar", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "es", "et", "fa", "fi", "fr", "gu", "he",
                        "hi", "hr", "hu", "id", "it", "ja", "kn", "ko", "lt", "lv", "mk", "ml", "mr", "ne", "nl", "no", "pa", "pl",
                        "pt", "ro", "ru", "sk", "sl", "so", "sq", "sv", "sw", "ta", "te", "th", "tl", "tr", "uk", "ur", "vi", "zh-cn", "zh-tw")

        
        self.register_admin_command(ModuleAdminCommand(
            'listlangs',
            self._list_langs,
            usage = f"{self.module_name} listlang",
            description = "List all languages."
            ))
        self.register_admin_command(ModuleAdminCommand(
            "outlang",
            self._out_lang,
            usage  = f"{self.module_name} outlang",
            description = "lists current output languages set."            
        ))
        
        self.register_admin_command(ModuleAdminCommand(
            "account",
            self._set_translate_account,
            usage = f"{self.module_name} account",
            description = "Use to set the response account" 
        ))
        
        self.register_admin_command(ModuleAdminCommand(
            "addoutlang",
            self._add_out_lang,
            usage  =  f"{self.module_name} addoutlang en",
            description =  "Add a language to translate to"
        ))
        
        self.register_admin_command(ModuleAdminCommand(
            "removeoutlang",
            self._remove_out_lang,
            usage = f"{self.module_name} removeoutlang fr",
            description =  "Remove a output language"
        ))
        
        self.register_admin_command(ModuleAdminCommand(
            "setprefix",
            self._set_prefix,
            usage = f"{self.module_name} setprefix ^ in [lang]: ",
            description = "set the response prefix"
        ))
        
        if  not 'outlangs' in self._module_data:
            self._module_data["outlangs"] = []
            self._module_data["outlangs"].append("en") 
        if not 'prefix' in self._module_data:
            self._module_data["prefix"] =""
                
        
        self.event_listen(EVT_CHATMESSAGE, self.chat_message)
        self.save_module_data(self._module_data)
    
    def chat_message(self, event):
        self._module_data =  self.get_module_data()
        #self.print(self._module_data)
        
        curlang = langid.classify(event.message)
       # self.print(curlang)
        if not curlang in self._module_data["outlangs"] or curlang[1]>1:
            response_twitch_id  =  self._module_data["account"]
            prefix = self._module_data["prefix"].replace("[lang]",curlang[0])
            
            for i in self._module_data["outlangs"]:
                translator  =  Translator()
                message = translator.translate(text=event.message,dest=i,src=curlang[0]).text
                if not message in event.message: 
                    self.send_chat_message(f"{message}",event=event,twitch_id=response_twitch_id)
                else:
                    return
        elif curlang[1] < -1:
            for i in self._module_data["outlangs"]:
                translator = Translator()
                translated = translator.translate(text=event.message,dest=i)
                
                if not translated.text in event.message:
                    prefix = self._module_data["prefix"].replace("[lang]",translated.src)
                    self.send_chat_message(f"{prefix} {translated.text}")
                else:
                    return
                

    def  _list_langs(self, input, command):
        self.print(self.langs)
        
    def _out_lang(self, input, command):
        self.print(self._module_data["outlangs"])
    
    def _add_out_lang(self,input,command):
        input = input.strip()
        if  input in self.langs:
            if not input in self._module_data["outlangs"]:
                self._module_data["outlangs"].append(input)
                self.save_module_data(self._module_data)
                self.print(f"{input} added to outlangs")
            else:
                self.print(f"{input} already in output languages.")
            
        else:
            self.print(f"{input} is not a valid language.")
        
    def _remove_out_lang(self,input,command):
        input =  input.strip()
        
        if input in self.langs:
            if input in self._module_data["outlangs"]:
                self._module_data["outlangs"].remove(input)
                self.save_module_data(self._module_data)
                self.print(f"{input} removed successfully.")
            else:
                self.print(f"{input} not in outlangs.")
        else:
            self.print(f"{input} not a valid language")
     
    def _set_prefix(self,input,command):
        
        if not input == self._module_data["prefix"]:
            self._module_data["prefix"] = input
            self.save_module_data(self._module_data)
            self.print(f'"{input}" set as response prefix.')
        else:
            self.print(f'"{input}" already the set response prefix.')
             
        
    def _set_translate_account(self,input,command):

        def account_selected(account):
            self._module_data['account'] = account.twitch_user_id
            self.save_module_data(self._module_data)
            self.print(f"Response account set to {account.display_name}")


        self.select_account(account_selected)
        


    def shutdown(self):
        self.save_module_data(self._module_data)

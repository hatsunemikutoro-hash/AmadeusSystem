import time
import asyncio
import pyperclip

from textual.app import App
from textual.widgets import Header, Footer, Static, Input
from textual.containers import VerticalScroll

# Certifique-se de que seus imports internos continuam aqui
from kurisu.brain_func.core import falar, memory
from kurisu.memory.memory_manager import wipe, mudar_persona

# =========================
# CONFIG
# =========================

MAX_MESSAGES = 150  # limite de widgets mantidos no histórico (perf)
STREAM_FLUSH_INTERVAL = 0.05  # segundos entre atualizações de tela durante o streaming
SCROLL_TOLERANCE = 3  # linhas de folga para considerar "no final" do scroll

# =========================
# ASCII BANNERS
# =========================

KURISU_BANNER = r"""[bold #FFD700]
                                                     :
                                                   :::
                      -:::----::::               :-*%- 
                 -:-+*%%%@%%%@@%*%#+:::        --*@@#- 
              :-=*@@##@@%@%%#@%*+@@%+%#--:   --+@@@@*- 
            :-*%*#*%@*+++++++++++#%#@@###*-:=*@@@@@@+: 
           -*@*@@%*=*#+=--+@@@@#-+#==*%@@@@*+@@@@@@%-  
         :=*%@@%+*@@+::::::---=-::::+*=#@@@=%@@@@@@+:  
        -=@@@#=+@@@%+:::::::::::::::-#@%=++@@@@@@@#:   
       :=%#*%=%--*-::::::::::::::::::+@@=#@@@@@@@=#%:    
      :-%@@@+#-::::::::=*%@@@@%*=:::::-+@@@@@*+@+-:    
      :%#%#+*=:::::::=@@@@@@@@@@@%=::=%@@@@#+%@@#-     
     :=@@@%-@#=:::::+@@@@@@@@@@@@@#=%@@@@#-#+@@@%=     
     :*@@@**@@#::::=%@@@@@@@@@@@%+#@@@@#-:-#@@+*##%+:    
     :*@@@+#@@*::::=@@@@@@@@@@#=%@@@@#-:-#@@+*##%+:     
     :*@@@**+::::::-%@@@@@@@*=%@@@@*::::-%@@=#%%#=      
     :=@@@%-#-::::::=@@@@%+*@@@@%++-:::::=*#+@@@%=       
      :#@@@**+:::::::-#*=@@@@@*=%#-:::::::#-#+%**-        
      :-@@@@+*+*#-:::=*@@@@#==*=::::::::-*=#%@@@=:       
       :=@@@@+#@@*-*@@@@#=-:::::::::-##+++*##%@=:        
       :=+@@***-+@@@@#-:::::::::::-%@@@#=#@@@@-:         
     :-#++=*%%@@++++=:::=*++=::::::*@*+##*#*%=:          
    -=%#-*%*+@%#@@#==*%#@@@@@=-+%#+=*%%@@*%=-            
    -#@%#+-:::+@@#@#@%*+=-=====+#*#@@%##%+-              
    ::-:       :=+#@@#%@@+#%@%#%@#@#@%+-:                
                  :--+#@@@#@@%*@@#=--:                   
                       ::::::::::                     [/]"""

VALKYRIE_BANNER = r"""[bold #00A8FF]
                      -  -@@:  =                  
            .#-  @@@:@@@%:@@@  =#             
           :@@@@%@@@@@@@@@@@@#@@@@            
       #@@++@@@@@@@@@@@@@@@@@@@@@@-+@@*       
     .  %@@@@@@@@@@@#*==+*@@@@@@@@@@@@        
    =@@@@@@@@@@#              #@@@@@@@@@@#    
     #@@@@@@@.       @@@%        @@@@@@@#     
  @@@@@@@@@-  @%  @@@@@@@@@@ .@@. .@@@@@@@@@  
  .@@@@@@@   @@@@@@@@@@@@@@@@@@@@.  %@@@@@@.  
   .@@@@@.    %@@@@@@%==#@@@@@@@     @@@@@+:. 
#@@@@@@@+   -@@@@@@        #@@@@@=   :@@@@@@@#
 .@@@@@@. ##%@@@@@   .##-   *@@@@%##  @@@@@@. 
.@@@@@@@. @@@@@@@*   @@@@-  -@@@@@@@  @@@@@@@ 
@@@@@@@@. %%%@@@@@    %%:   @@@@@@%%  @@@@@@@%
   :@@@@+   .@@@@@@.       #@@@@@:   +@@@@:   
  +@@@@@@.    %@@@@@@@#+%@@@@@@@    .@@@@@@+  
 :@@@@@@@@   @@@@@@@@@@@@@@@@@@@@.  @@@@@@@@. 
     +@@@@@:  %@: @@@@@@@@@@.:@@  -@@@@@#     
    *@@@@@@@@       .@@@@        @@@@@@@@@    
    .--:*@@@@@@+              -@@@@@@*.-#+    
       =@@@@@@@@@@@+.     =%@@@@@@@@@@=       
       =@%::@@@@@@@@@@@@@@@@@@@@@@:-@@+       
           :@@@@@@@@@@@@@@@@@@@@@@.           
             :.  @@@-@@@@:@@@  .:             
                 :=  +@@=  #:                 
[/]"""

SKULD_BANNER = r"""[bold #00FF66]

                :%+.       +%-                
               :@@@@%+::=%@@@@:               
               #@@@@@@@@@@@@@@%.              
              -@@@@@@@@@@@@@@@@+              
              @@@@@@@@@@@@@@@@@@              
              -#@@@@@@@@@@@@@@#-              
      :-=#@# :.  :+%@@@@@@%+:  .- *@#=-:      
    .%@@@@@- +@@*:          :*%@+ .@@@@@%.    
      *@@@@@-  .=#@@@#++*%@@#+.  :%@@@@*      
        -%@@@@#-    :-==-:    -*@@@@%=        
           =+@@@@@%=------=%@@@@@*=           
             -::==+#%@@@@%#+==-:-             
           : *@@@%#=-------*%@@@* :           
         +@@+ @@@@@@@@@@@@@@@@@@.+@@*         
       .+@@@@-:@@@@@@@@@@@@@@@@--@@@@+.       
          -%@@=.#@@@@@@@@@@@@#:=@@@-          
       .:-*%@@@%:=@@@@@@@@@@+:%@@@@*-::.      
    *@@@@@@@@@@@#-*@@@@@@@@#-#@@@@@@@@@@@*    
     -%@@@@@@@@@@+=@@@@@@@@++@@@@@@@@@@@-     
       +@@@@@@@@@@+*@@@@@@*+@@@@@@@@@@+       
         +%@@@@@@@@*#@@@@#*@@@@@@@@@+         
           .+%@@@@@@@@@@@@@@@@@@%+.           
               .=+*%%@@@@%%*+=.               

[/]"""


# =========================
# HELPERS
# =========================

def get_prefix(persona: str) -> str:
    if persona == "valkyrie":
        return "[bold #00A8FF]Amadeus // Valkyrie: [/bold #00A8FF] "
    elif persona == "skuld":
        return "[bold #00FF66]Amadeus // Skuld: [/bold #00FF66] "
    elif persona == "gold":
        return "[bold #ffc300]Amadeus // GOLD: [/bold #ffc300] "
    return "[bold #FF003C]Amadeus // Kurisu: [/bold #FF003C]"


# =========================
# APP
# =========================

class AmadeusKurisu(App):
    BINDINGS = [
        ("ctrl+y", "copy_last", "Copiar Última Resposta"),
        ("ctrl+v", "paste_last", "Colar da área de transferência"),
    ]

    CSS = """
    Screen { 
        background: #05050A; 
    }

    #chat_container {
        height: 1fr;
        border: ascii #FF003C;
        background: #0A0A0A;
        padding: 1 2; 
        overflow-y: auto;
    }

    #chat_container.theme-valkyrie { border: solid #00A8FF; }
    #chat_container.theme-skuld { border: hkey #00FF66; }
    #chat_container.theme-gold { border: round #ffe900; }

    .msg_user { 
        margin-top: 1; 
        text-style: bold;
    }

    .msg_amadeus { 
        margin-top: 0;
    }

    .msg_info { 
        margin-top: 1;
        margin-bottom: 1; 
        text-align: left;
    }

    .ascii_art {
        text-align: center;
        margin-top: 2;
        margin-bottom: 1;
    }

    #status_bar {
        height: 1;
        background: #11111A;
        color: #ff00ff;
        padding-left: 2;
        text-style: italic;
    }

    Input {
        border: round #FF003C;
        background: #0D0D0D;
        color: #ffa400;
        padding-left: 1;
    }

    Input.theme-valkyrie { border: round #00A8FF; }
    Input.theme-skuld { border: round #00FF66; }
    Input.theme-gold { border: round #ffe900; }

    Input:disabled {
        opacity: 0.5;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ultima_resposta_amadeus = ""
        self.current_persona = "kurisu"
        self._processing = False

    # UI SETUP

    def compose(self):
        yield Header()

        with VerticalScroll(id="chat_container"):
            pass

        yield Static(id="status_bar")
        yield Input(placeholder="user@makise-lab:~$", id="terminal_input")
        yield Footer()

    async def on_mount(self):
        container = self.query_one("#chat_container", VerticalScroll)

        await container.mount(Static(KURISU_BANNER, markup=True, classes="ascii_art"))
        await container.mount(
            Static(
                "[bold #ff7700]>>> Amadeus ONLINE System - Makise Kurisu Base Load[/bold #ff7700]",
                markup=True,
                classes="msg_info"
            )
        )
        self.query_one("#terminal_input", Input).focus()

    # helpers
    def _is_scrolled_to_bottom(self, container: VerticalScroll) -> bool:
        """Só forçamos o auto-scroll se o usuário já estiver perto do final.
        Evita 'puxar' a tela de quem subiu pra reler algo."""
        max_offset = container.scrollable_content_region.height
        return (container.scroll_y + container.size.height) >= (
                container.virtual_size.height - SCROLL_TOLERANCE
        )

    async def _mount_message(self, widget: Static, container: VerticalScroll, force_scroll: bool = True):
        was_at_bottom = self._is_scrolled_to_bottom(container) if not force_scroll else True
        await container.mount(widget)

        # Poda o histórico antigo para não acumular widgets indefinidamente
        children = container.children
        if len(children) > MAX_MESSAGES:
            overflow = len(children) - MAX_MESSAGES
            for child in children[:overflow]:
                await child.remove()

        if force_scroll or was_at_bottom:
            container.scroll_end(animate=False)

    # =========================
    # SPINNER
    # =========================

    async def run_spinner(self, status):
        spinner = "|/-\\"
        i = 0

        while True:
            nome = self.current_persona.capitalize()
            status.update(
                f"[bold #ff7700]{spinner[i % 4]} Amadeus {nome} is Processing..."
            )
            i += 1
            await asyncio.sleep(0.1)


    def action_copy_last(self):
        if self.ultima_resposta_amadeus:
            pyperclip.copy(self.ultima_resposta_amadeus.strip())
            self.notify("Response copied to the clipboard!", title="Amadeus OS")
        else:
            self.notify("Empty buffer.", severity="warning", title="Amadeus OS")

    def action_paste_last(self):
        try:
            text = pyperclip.paste()
            if not text:
                return

            input_box = self.query_one("#terminal_input", Input)
            pos = input_box.cursor_position

            v = input_box.value
            input_box.value = v[:pos] + text + v[pos:]
            input_box.cursor_position = pos + len(text)
            input_box.focus()

        except Exception as e:
            self.notify(str(e), severity="error")

    async def processar_comando(self, comando: str):
        container = self.query_one("#chat_container", VerticalScroll)
        input_box = self.query_one("#terminal_input", Input)

        cmd = comando.split()[0].lower()

        if cmd == "/wipe":
            wipe()
            memory.clear()
            await self._mount_message(
                Static("[dim]--- Temporal memory erased ---[/dim]", classes="msg_info"),
                container,
            )
            return

        mapa = {
            "/k": (
                "kurisu",
                "[bold #FF003C]✦ Kurisu took over the conversation[/bold #FF003C]",
                "theme-kurisu",
                KURISU_BANNER
            ),
            "/v": (
                "valkyrie",
                "[bold #00A8FF]Ψ Valkyrie took on the engineering mission[/bold #00A8FF]",
                "theme-valkyrie",
                VALKYRIE_BANNER
            ),
            "/s": (
                "skuld",
                "[bold #00FF66]Φ Skuld took on the survival mission[/bold #00FF66]",
                "theme-skuld",
                SKULD_BANNER
            ),
            "/g": (
                "gold",
                "[bold #ffc300]YOU'RE INDESTRUCTABLE.[/bold #ffc300]",
                "theme-gold",
                KURISU_BANNER
            )
        }

        if cmd not in mapa:
            return

        persona, msg, theme, banner = mapa[cmd]

        if self.current_persona == persona:
            return

        self.current_persona = persona
        mudar_persona(persona)

        container.remove_class("theme-valkyrie", "theme-skuld")
        input_box.remove_class("theme-valkyrie", "theme-skuld")

        if persona != "kurisu":
            container.add_class(theme)
            input_box.add_class(theme)

        await self._mount_message(Static(banner, markup=True, classes="ascii_art"), container)
        await self._mount_message(Static(msg, classes="msg_info"), container)

    async def on_input_submitted(self, event: Input.Submitted):
        user_text = event.value.strip()
        if not user_text or self._processing:
            return

        container = self.query_one("#chat_container", VerticalScroll)
        status = self.query_one("#status_bar", Static)
        input_box = self.query_one("#terminal_input", Input)

        event.input.value = ""

        if user_text.startswith("/"):
            await self.processar_comando(user_text)
            return

        await self._mount_message(
            Static(f"[bold #00ff94]user@makise-lab:~[/bold #00ff94]$ {user_text}", classes="msg_user"),
            container,
        )

        prefix = get_prefix(self.current_persona)

        amadeus_msg = Static(prefix, classes="msg_amadeus")
        await self._mount_message(amadeus_msg, container)

        self._processing = True
        input_box.disabled = True

        spinner_task = asyncio.create_task(self.run_spinner(status))

        start = time.perf_counter()
        current = prefix
        raw = ""
        last_flush = 0.0

        try:
            async for chunk in falar(user_text):

                if not spinner_task.done():
                    spinner_task.cancel()
                    status.update("")

                current += chunk
                raw += chunk

                now = time.perf_counter()
                if now - last_flush >= STREAM_FLUSH_INTERVAL:
                    amadeus_msg.update(current)
                    if self._is_scrolled_to_bottom(container):
                        container.scroll_end(animate=False)
                    last_flush = now

            # flush final para garantir que o último trecho apareça
            amadeus_msg.update(current)
            if self._is_scrolled_to_bottom(container):
                container.scroll_end(animate=False)

            self.ultima_resposta_amadeus = raw

            latency = time.perf_counter() - start

            await self._mount_message(
                Static(f"[dim]latency: {latency:.3f}s[/dim]", classes="msg_info"),
                container,
            )

        except Exception as e:
            if not spinner_task.done():
                spinner_task.cancel()

            status.update("[bold red]CRITICAL ERROR[/bold red]")

            await self._mount_message(
                Static(f"[bold red]Exception Triggered: {e}[/bold red]", classes="msg_info"),
                container,
            )

        finally:
            self._processing = False
            input_box.disabled = False
            input_box.focus()


if __name__ == "__main__":
    AmadeusKurisu().run()
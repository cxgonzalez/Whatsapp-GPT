import signal
import time
import keyboard
import re
import emoji

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from openai import OpenAI
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from IPython.display import clear_output

PATH="C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome()
driver.get("https://web.whatsapp.com/")
driver.maximize_window()

# Timer for the QR login before doing everything else. Not doing it in time should raise an error later when trying to access certain xpaths
time.sleep(20)

# List of names to which you want to send the message
namelist = ["##CONTACT NAME##"]
bot_name = "YourNameBOT"
activity = "coding and improving my latest chatbot"
main_description = "I'm just some dude that looks at data, interpret it, then proceed to program things."
messages = [
    {"role" : "system", "content" : f"""You're {bot_name}. Your task is to replace me while i'm {activity}. Your answers will
    be directly sent to {namelist[0]}'s Whatsapp Chat. When doing so, you must pretend to be me. Here's a little description
    of me, for you to follow:
    '{main_description}'
    Unfortunately, you can't currently process images nor stickers. When you receive those, you'll receive the message [[IMAGE OR STICKER]]
    instead. Notify your inability to process those whenever you receive them."""}
]

client = OpenAI(api_key="YOUR-API-KEY")

# Variables for interruption of the program
run_bot = True
num_presses = 0
last_press_time = time.time()

# This is what will 
def on_keyboard_interrupt(e):
    global run_bot, num_presses, last_press_time
    current_time = time.time()
    
    if e.event_type == keyboard.KEY_DOWN and (e.name == '5'):
        if current_time - last_press_time > 0.1:  # This is so it counts 1 press every 0.1 seconds.
            num_presses += 1
            last_press_time = current_time
            remaining_presses = max(0, 5 - num_presses)
            print(f"Press '5' at least {remaining_presses} more times to stop the execution.")
            if num_presses >= 5:
              print("The execution will stop. Please wait, this could take a minute...")
              run_bot = False

# Signals config
signal.signal(signal.SIGINT, signal.SIG_IGN) 

# Keyboard listener (so it can receive the stopping signals)
keyboard.hook(on_keyboard_interrupt)

# Main Loop
while run_bot:
    for name in namelist:
        # Find and click on the contact search-bar 
        getsearchbox = driver.find_element("xpath", "/html/body/div[1]/div/div[2]/div[3]/div/div[1]/div/div[2]/div[2]/div/div[1]/p")
        getsearchbox.click()
        time.sleep(2)
        
        # Type the name of contact
        getsearchbox.send_keys(name)
        time.sleep(5)
        
        unreadMsgs=False
        for i in range(100):
            div_num = str(i)
            chat_title = "???"
            try:
                getlist = driver.find_elements("xpath", f"/html/body/div[1]/div/div[2]/div[3]/div/div[2]/div[1]/div/div/div[{div_num}]/div/div/div/div[2]/div[1]/div[1]")
                initial_soup = getlist[0].get_attribute('innerHTML')
                cooked_soup = BeautifulSoup(initial_soup)
                chat_title = cooked_soup.find_all(attrs={'aria-label': ''})[0].text
            except:
                pass
            if(chat_title==name):
                print(chat_title + " was found!!!")
                break
            else:
                print("Found "+chat_title+". Still looking ...")
                
        getlist=driver.find_elements("xpath", f"/html/body/div[1]/div/div[2]/div[3]/div/div[2]/div[1]/div/div/div[{div_num}]/div/div/div/div[2]/div[2]/div[2]/span[1]/div")
        try:
            n_unread = int(BeautifulSoup(getlist[0].get_attribute('innerHTML')).find_all(attrs={'aria-label': re.compile('nread.*')})[0].text)
        except:
            n_unread = 0
        print("Unread messages: "+str(n_unread))
        if(n_unread>0):
            getlist[0].click()
            time.sleep(3)
            ### Reading last n messages (n = total unread identified)
            get_msgs = driver.find_elements("xpath", "/html/body/div[1]/div/div[2]/div[4]/div/div[2]/div/div[2]/div[3]")
            last_index = len(get_msgs[0].find_elements("xpath", "./div"))
            final_message = ''
            for i in range(n_unread):
                try:
                    looking_author = driver.find_elements("xpath", f"/html/body/div[1]/div/div[2]/div[4]/div/div[2]/div/div[2]/div[3]/div[{last_index-n_unread+i+1}]/div/div/div[1]/div[1]")
                    author_soup = BeautifulSoup(looking_author[0].get_attribute('innerHTML'))
                    name_extract = author_soup.find('span')
                    author = name_extract['aria-label'].replace(":","")
                    if author==name:
                        role = "user"
                    else:
                        role = "assistant"        
                    get_new_msg = driver.find_elements("xpath", f"/html/body/div[1]/div/div[2]/div[4]/div/div[2]/div/div[2]/div[3]/div[{last_index-n_unread+i+1}]/div/div/div[1]/div[1]/div[1]/div/div[1]/div/span[1]")
                    pre_soup = get_new_msg[0].get_attribute('innerHTML')
                    beautisoup = BeautifulSoup(pre_soup, 'lxml')
                    i_message = beautisoup.find_all(attrs={'aria-label': ''})[0]
                    soup = BeautifulSoup(str(i_message), 'html.parser')
                    text_element = soup.find('span')
                    msg_contents = ''.join(map(str, text_element.contents))
                    emojis_alt = [img['alt'] for img in soup.select('img[class*=emoji]')]
                    msg_contents_emoji = msg_contents
                    for emoji_alt in emojis_alt:
                        img_tag = soup.find('img', alt=emoji_alt)
                        msg_contents_emoji = msg_contents_emoji.replace(str(img_tag), emoji_alt, 1)
                except:
                    msg_contents_emoji = '[[IMAGEN o STICKER]]'
                final_message = final_message + msg_contents_emoji + ' '
            messages.append({'role' : 'user', 'content' : final_message})
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            
            ### ESCRITURA DE RESPUESTA
            chat_box = driver.find_element("xpath", "/html/body/div[1]/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div[2]/div[1]")
            chat_box.click()
            bot_answer = response.choices[0].message.content
            bot_answer = emoji.replace_emoji(bot_answer, replace='')
            chat_box.send_keys(bot_answer)
            messages.append({'role' : 'assistant', 'content' : bot_answer})
            time.sleep(2)
            chat_box.send_keys(Keys.ENTER)
            driver.find_element("xpath","/html/body").click()
            time.sleep(1)
            driver.find_element("xpath","/html/body").send_keys(Keys.ESCAPE)
        else:
            driver.find_element("xpath","/html/body/div[1]/div/div[2]/div[3]/div/div[1]/div/div[2]/span/button/span").click()
            time.sleep(2)
            driver.find_element("xpath","/html/body").click()
            time.sleep(2)
            driver.find_element("xpath","/html/body").send_keys(Keys.ESCAPE)
        
        
    time.sleep(40)  # Time before starting over again
    clear_output(wait=True)

### AFTER THE BOT IS STOPPED THROUGH THE KEYBOARD COMMAND, IT WILL SUMMARIZE THE CONVERSATION
summary_input = ''
for i in range(len(messages)):
    if messages[i]['role']=='user':
        summary_input = summary_input + namelist[0] + ': '
        summary_input = summary_input + messages[i]['content'] + '\n'
    elif messages[i]['role']=='assistant':
        summary_input = summary_input + bot_name + ': '
        summary_input = summary_input + messages[i]['content'] + '\n'
    else:
        pass

summary_gpt = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role" : "system", "content": f""""You will receive a conversation between {namelist[0]} and {bot_name}.
                Summarize in no more than 3 very concise key points the most relevant content of the conversation. """},
                         {"role": "user", "content" : summary_input}]
)

# Disabling listener and closing Chrome
keyboard.unhook_all()
driver.close()

# Notification plus summary
print("The ChatBOT was manually stopped. Here's a summary of the conversation:")
print(summary_gpt.choices[0].message.content)

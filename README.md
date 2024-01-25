# Whatsapp-GPT

A Selenium powered Whatsapp automation, which checks periodically a specific contact, goes into the chat if there are unread messages, then answers in your place.
How good it is at pretending to be you, depends entirely on the prompt of course.

## ... but Why?
This came as an idea for when you're not available. If you went to the supermarket, or washing dishes, or cooking lunch or whatever, just specify so! Then your GPT powered clone
will keep the conversation going. Hopefully!

That being said, this was also an exercise for me to get into the OpenAI API world. There are more things that i'd love to explore, but this was the funniest idea that i had at the moment.
From "a fixed automated response" to "what if it could interact? lets put some AI in it" to "what if i asked him to act like me?". That was pretty much my thought process. I've seen approaches to the
first one, but didnt find AI approaches. Not saying that there are not, just that i didn't find them! (and come on, it's funnier to program it yourself)

## ...ok, sure. So, what does it do? What does it need?
Mainly:
  - A single contact name inside a list (planning to expand, hence the list, but not there yet!)
  - Name the bot! (Don't leave it as is, give it some personality through a name!)
  - Your current activity. The reason for absence. Just for him to have more information to chat
  - A description (of its personality). The purpose is to replace you while you're away, so usually is a self-description. But doesn't HAVE to be. Just be sure to edit the prompt (which includes the 'pretend to be me' instruction by default)

Once that is set and you run it, just log in via QR to WhatsappWeb and its done. Since opening, there's like a 20s window to log in.

## What about the specifics?
Once in, it will iterate over the whole post-login process every minute or so. This post-login process consists in:
  1. Going to the search bar and typing the contact name
  2. Iterate over the search results until it find a name that matches the given contact name (to make sure it does go directly into a random group to which the contact belongs)
  3. Checks if there are any unread messages (through the green circle)
  4. If there's none, then deletes the search bar contents and gets out of it (Then skips to 10.)
  5. If there are, it will take the contents of that element (AKA the number of unread messages) and save it as a variable (say, 'n_unread')
  6. Gets into the chat and iterates over the last 'n_unread' messages, then concatenates into one.
  7. This concatenation is then appended to the messages list, under the 'user' role, for the OpenAI API to consume.
  8. Once consumed and a response was generated, it is written and sent. It is also appended to messages under the 'assistant' role of course!
  9. Exit the chat
  10. Enters a 40s time.sleep before iterating again

## This is cool! But now i'm trapped and i dont feel like closing the windows or resetting the kernel or...
Worry not! There's a command for that. In fact, you're encouraged to use it! All you have to do is press the '5' key, 5 times. 
When doing so, the bot will print a notification about the manual stop being activated. When ready, it will exit the post-login iteration.
And here's the catch! When it does, it takes the messages object and summarizes it! So if you were away for like 1 hour, just manually stop it and you'll get a
nice and tidy bullet list with your summary.

## This sounds perfect, way too perfect even...
Well, far from it! There are many pending fixes. Some of those that i know of/can think of are:
  - Iterate over a list of contacts, each with their own history. I thought of a dictionary approach, using the contact name as a key to get a messages object for each, but its kinda tricky when you think about the prompts and how to be flexible. You wouldn't want to mix up how you talk to your partner, your best friend and your family!
  - Right now the prompt includes a statement for "you can't see images nor sticker but here's what you'd see if you get those". That works just fine, but it would be nice if it could. Not a priority though.
  - RECEIVING MESSAGES WHILE WRITING. **This is the main and biggest issue in my opinion**. If it counts the unreads, gets into the chat and then receives another new message before getting out of the chat, some messages will be lost. For instance, i have 3 unread messages, get into the chat with the '3' already saved and i get a 4th one. The bot will iterate over the last 3. So, from the now 4 new messages, it will read from 2 to 4, but not 1. It also messes up something else that i still can't quite catch, that when this happens, and it gets into the next iteration, it would retrieve a way older message (something like 20 messages ago) and respond to that.


But well, that's the work so far! I'll try to improve things whenever i can.

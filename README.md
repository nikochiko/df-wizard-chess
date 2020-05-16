# Wizard Chess w/ Dialogflow

[![Gitter](https://badges.gitter.im/wizard-chess/community.svg)](https://gitter.im/wizard-chess/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Build Status](https://travis-ci.com/nikochiko/df-wizard-chess.svg?branch=master)](https://travis-ci.com/nikochiko/df-wizard-chess)
[![codecov](https://codecov.io/gh/nikochiko/df-wizard-chess/branch/master/graph/badge.svg)](https://codecov.io/gh/nikochiko/df-wizard-chess)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=nikochiko/df-wizard-chess&identifier=259290685)](https://dependabot.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🤔 What is Wizard Chess? {: #what-is-wizard-chess }

To truly understand, I will have you read this

> **What do you do when you really want to play blindfold chess but
> you're stuck at home? 🏠**
>
> *Ask your chess friends - easy 👨‍👨‍👧‍👦*
>
> **They don't like blindfold 🤷**
>
> *Google for an online solution 💻, there are so many chess apps. There
> has to be one about blindfold chess.*
>
> **Pbbt 👅 There ain't one.**
>
> *What about.. the popular ones?*
>
> **They say "hide your pieces, it's just like blindfold chess 😇"**
>
> *Ugh - that's a scam*
>
> **I have to do something about this.. 👨‍🔧🍳**

Wizard Chess is **that** something. The goal is to provide the best
blindfold chess experience. That is, to have anything you might need
while playing blindfold chess - be it a platform to play, a platform to
learn, or a platform to further develop your prowess. See
[🧐 How do you do it?](#how-do-you-do-it) for the technical details.

Wizard Chess is already available as a Google Action! See
[🏄🏽‍♂️ Where can I play?](#where-can-i-play) to know more.

## 🧐 How do you do it? {: #how-do-you-do-it }

We use the wizardry 🔮 of AI assistants and chatbots to interact with the
user. When a user talks to our AI asssistant, the message is forwarded
to [Dialogflow](http://dialogflow.com/). It processes the request from
the assistant - intelligently, with machine learning - and sends it to
our [webhook](https://sendgrid.com/blog/whats-webhook/). Now our server
uses this cooked data to generate a response and sends it back to
Dialogflow which in turn sends it to the assistant. The whole process
basically looks like this:
```
    User ======= |AI assistant/chatbot| <-------> |Dialogflow| <-------> |THIS SERVER| 💪
```

Examples of operations done on our end are creating and storing chess
games in a database, receiving a move and updating the board
accordingly, and generating responses for the user.

## 🏄🏽‍♂️ Where can I play? {: #where-can-i-play }
The app is already available for the Google Assistant
[here](https://assistant.google.com/services/a/uid/0000003ba609b4ff?hl=en).
You can even launch the app without touching the link at all, just say
*Talk to Wizard Chess* to your Google Assistant to boot up the Action.

More platforms coming soon! Let me know via
[email](mailto:ktvm42@gmail.com) or
[Gitter](https://gitter.im/wizard-chess/community) if you want to see
Wizard Chess on a particular platform so that we can prioritize it.

## 📕 Usage guide {: #usage-guide }

Upon starting the Wizard Chess Action (by saying *Talk to Wizard
Chess*), you will be asked to choose the side you'd like to play as and
the assistant will present you with a list of three options: White,
Black and Random. Now you can either select an option by touch or say
your choice out loud. The latter even works with devices which don't
have a screen (e.g. Google Home).

The system to interpret moves is very lenient and allows you to choose
how you want to say the move. For example, you can describe your move
in:

- Long descriptive format - e.g. *Knight from g1 to f3* or *Pawn e4 captures d5* or even without mentioning the piece *d5 takes c4*
  - For pawn promotion, you can add the name of the promotion
    piece to the end - that is, *Pawn from d7 to d8 queen* or
    *b2 takes c1 queen*

- Shorter format with just the piece and square - e.g. *Knight to d4* or *Queen takes f6*
  - Pawn promotion is supported in the same way as above
  - Note that you will be notified by the assistant if your move
    is ambiguous. This usually means that there were more than one
    moves which matched your description - e.g. two knights which
    can come to the same square.

- Pawn moves by the squares they want to move to - e.g. *e4*, *g3*
- Castling - *castles*, *Castle short*, *Castle kingside*, *Long
  castling*, *Castle to the queen's side*
  - Note that simply saying *castle* without mentioning a side will
    castle on whichever side is legal, and defaulting to short castle if
    both are legal.
- Short Algebraic Notation (SAN) - e.g. *Bd6*, *Nbd7*
- Long Algebraic Notation (LAN) - e.g. *e2-e4*, *Nf6xe4*, *O-O*

Note: The app doesn't yet support descriptive moves like *Knight b to
d7* or *e takes d5*. In that case you should use the long descriptive
format of move by mentioning the actual square the piece was at - e.g.
*knight b8 to d7* and *e4 takes d5*

## 🔧 Contributing {: #contributing }

Use the [issue tracker](https://github.com/nikochiko/df-wizard-chess/issues) to suggest
new features or report bugs. Feel free to directly [create pull
requests](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request)
for small changes and typos. Create an issue before opening larger pull
requests so that the changes can be discussed beforehand. The latest
Dialogflow agent can be downloaded from \<link to be updated\>.

## ⏰ Changelog {: #changelog }

### 0.2.0 - 16/05/2020

- Moved from SQLite to Postgres with SQLAlchemy
- Bug fixes in show\_board
- Bug fixes with session\_id handling
- Added feature to accept SAN (or overspecified SAN) moves
- Fixed bug which caused stale result comment after engine's move
- Added feature to accept move when only a piece and square are
  mentioned
- Fixed bug which made app to crash when square had capital letters
  (A4, D5 etc.)
- Edited show board feature to flip board when user is playing as
  black

### 0.1.1 - 07/05/2020

- Set up Travis CI
- Set up coverage reporting with Codecov
- Moved from using Dict in memory to sqlite3 DB on disk 🎉
- Added testing to cover more than 90% of codebase 💪
- Added feature to see board at any time 👁️
- Board image will be shown after completion of games 📜

### 0.1.0 - 27/04/2020

- Format according to Black formatting tool
- Basic functionality to play a game as a Google Action
- Voice-activated ability to castle, promote pawn, and play move when
  at least the two squares involved in the move are given.
- Works with games stored in memory as Dict data type. Considering
  move to sqlite in future versions
- Unit tests added for most basic functions. More tests required for
  functions which handle intents.

## License {: #license }

Licensed under GNU General Public License 3.0 (GPL-3.0). See
[LICENSE](https://github.com/nikochiko/df-wizard-chess/blob/master/LICENSE)
for full text.

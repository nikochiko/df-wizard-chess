==========================
Wizard Chess w/ Dialogflow
==========================
.. image:: https://travis-ci.com/nikochiko/chess-server.svg?token=Tv6EyBGSze8NLsac3zQC&branch=master
    :target: https://travis-ci.com/nikochiko/chess-server
.. image:: https://codecov.io/gh/nikochiko/chess-server/branch/master/graph/badge.svg?token=HMjzAbiZU1
    :target: https://codecov.io/gh/nikochiko/chess-server
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

🤔 What is Wizard Chess?
=======================
To truly understand, I will have you read this

    **What do you do when you really want to play blindfold chess but you're stuck at home? 🏠**

    *Ask your chess friends - easy 👨‍👨‍👧‍👦*

    **They don't like blindfold 🤷**

    *Google for an online solution 💻, there are so many chess apps. There has to be one about blindfold chess.*

    **Pbbt 👅 There ain't one.**

    *What about.. the popular ones?*

    **They say "hide your pieces, it's just like blindfold chess 😇"**

    *Ugh - that's a scam*

    **I have to do something about this.. 👨‍🔧🍳**

Wizard Chess is **that** something. The goal is to provide the best blindfold chess experience.
That is, to have anything you might need while playing blindfold chess - be it a platform to play,
a platform to learn, or a platform to further develop your prowess. See `🧐 How do you do it?`_
for the technical details.

The app will first be made available as a Google Action.

🧐 How do you do it?
===================
We use the wizardry 🔮 of AI assistants and chatbots to interact with the user. When a user talks to
our AI asssistant, the message is forwarded to `Dialogflow <http://dialogflow.com/>`_. It
processes the request from the assistant - intelligently, with machine learning - and sends it to our
`webhook <https://sendgrid.com/blog/whats-webhook/>`_. Now our server uses this cooked data to generate
a response and sends it back to Dialogflow which in turn sends it to the assistant. The whole process
basically looks like this:
::
    User ======= |AI assistant/chatbot| <-------> |Dialogflow| <-------> |THIS SERVER| 💪

Examples of operations done on our end are creating a new chess game, or receiving a move, updating the
game board on our side and giving back a response. Or say a user has forgotten the board, in that case
we save an image of the board and show it to the user.

⏰ Changelog
============

Next release (v0.2.0)
---------------------
* Moved from SQLite to Postgres with SQLAlchemy
* Bug fixes in show_board
* Bug fixes with session_id handling
* Add feature to accept SAN (or overspecified SAN) moves
* Fix bug which caused stale result comment after engine's move

v0.1.1 - 07/05/2020
-------------------
* Set up Travis CI
* Set up coverage reporting with Codecov
* Moved from using Dict in memory to sqlite3 DB on disk 🎉
* Added testing to cover more than 90% of codebase 💪
* Added feature to see board at any time 👁️
* Board image will be shown after completion of games 📜


v0.1.0 - 27/04/2020
-------------------
* Format according to Black formatting tool
* Basic functionality to play a game as a Google Action
* Voice-activated ability to castle, promote pawn, and play move when at least the two squares involved in the move are given.
* Works with games stored in memory as `Dict` data type. Considering move to sqlite in future versions
* Unit tests added for most basic functions. More tests required for functions which handle intents.
* TODOs for next minor:
    * Add show_board intent to display the current board as an image.
    * Display board after game has ended
    * Store games in a database instead of Dict
    * Add support for simple SAN notation - intent, entity, intent-handler
    * Add support for when one piece and one square are mentioned - tell the user if move is ambiguous
    * Setup Travis CI with flake8 and coverage tools and cover at least 80% with unit tests

==========================
Wizard Chess w/ Dialogflow
==========================
.. image:: https://badges.gitter.im/wizard-chess/community.svg
    :target: https://gitter.im/wizard-chess/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge
.. image:: https://travis-ci.com/nikochiko/df-wizard-chess.svg?token=Tv6EyBGSze8NLsac3zQC&branch=master
    :target: https://travis-ci.com/nikochiko/df-wizard-chess
.. image:: https://codecov.io/gh/nikochiko/df-wizard-chess/branch/master/graph/badge.svg?token=HMjzAbiZU1
    :target: https://codecov.io/gh/nikochiko/df-wizard-chess
.. image:: https://api.dependabot.com/badges/status?host=github&repo=nikochiko/df-wizard-chess&identifier=259290685
    :target: https://dependabot.com
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

Wizard Chess is already available as a Google Action!
See `🏄🏽‍♂️ Where can I play it?`_ to know more.

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

Examples of operations done on our end are creating and storing chess games in a database,
receiving a move and updating the board accordingly, and generating responses for the user.

🏄🏽‍♂️ Where can I play it?
=======================
The app is already available for the Google Assistant `here <https://assistant.google.com/services/a/uid/0000003ba609b4ff?hl=en>`_.
More platforms coming soon! Let me know via `email <mailto:ktvm42@gmail.com>`_ or `Gitter <https://gitter.im/wizard-chess/community>`_
if you want to see Wizard Chess on a particular platform so that we can prioritize it.

🔧 Contributing
==============
Use the `issue tracker <https://github.com/nikochiko/df-wizard-chess/issues>`_ to suggest new features
or report bugs.
Feel free to directly `create pull requests <https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request>`_
for small changes and typos. Create an issue before opening larger pull requests so that the changes
can be discussed beforehand.
The latest Dialogflow agent can be downloaded from <link to be updated>.

⏰ Changelog
============

Next release (v0.2.0)
---------------------
* Moved from SQLite to Postgres with SQLAlchemy
* Bug fixes in show_board
* Bug fixes with session_id handling
* Added feature to accept SAN (or overspecified SAN) moves
* Fixed bug which caused stale result comment after engine's move
* Added feature to accept move when only a piece and square are mentioned
* Fixed bug which made app to crash when square had capital letters (A4, D5 etc.)
* Edited show board feature to flip board when user is playing as black

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

License
=======
Licensed under GNU General Public License 3.0 (GPL-3.0). See `LICENSE <https://github.com/nikochiko/df-wizard-chess/blob/master/LICENSE>`_
for full text.

import discord
import tinydb
import re
import poll as polllib


class PollManager:
    commandWords = {"vote": "vote"}
    _tableName = "polls"

    def __init__(self, db: tinydb.TinyDB):
        self.table = db.table(self._tableName)

    def processMessage(self, message: discord.Message):
        author: int = message.author.id
        # Remove command prefix
        msg = re.sub("^.*"+self.commandWords.get("vote"), "", message.content, 1).strip()

        # get current command option
        cmdoption, cmdargs = msg.split(" ", 1)
        cmdoption = cmdoption.lower()

        # Create a new poll
        if cmdoption.startswith("new") or cmdoption.startswith("create"):
            multivote: bool = False
            editable: bool = True
            showAuthors: bool = False
            showVotes: bool = False
            canVoteNow: bool = True
            question: str = ""
            options: [] = []
            poll = polllib.Poll(author, question, multivote, editable, showVotes, showAuthors, canVoteNow, options)
            id = self.table.insert(poll)
            return await message.channel.send('Poll created: ||%{0}|| {1.question}'.format(id, poll))

        # Show all polls
        if cmdoption.startswith("history"):
            output = "Historical Polls:"
            output += "\n-----------------"
            polls = self.table.all()
            for poll in polls:
                output += "\n\|\| ||%{0}|| \|\| {1.question}".format(polls.index(poll), poll)
            output += "\n-----------------"
            return await message.channel.send(output)

        # Show current polls
        if cmdoption.startswith("current") or cmdoption.startswith("active"):
            output = "Current Polls:"
            output += "\n-----------------"
            polls = self.table.all()
            for poll in polls:
                if not poll._finished:
                    output += "\n\|\| ||%{0}|| \|\| {1.question}".format(polls.index(poll), poll)
            output += "\n-----------------"
            return await message.channel.send(output)

        # Perform an operation for an existing poll
        # Allow % prefix or no prefix
        if cmdoption.startswith("%"):
            cmdoption = cmdoption.replace("%", "")
        if cmdoption.isnumeric():
            poll: polllib.Poll = self.table.get(int(cmdoption))

            # Verify a poll was found
            if not poll:
                return await message.channel.send('Unknown Poll ID!')

            # get subcommand option and args
            cmdoption, cmdargs = cmdargs.split(" ", 1)
            cmdoption = cmdoption.lower()

            # add an option to the poll
            if cmdoption.startswith("add"):
                if poll.addOption(author, cmdargs):
                    return await message.channel.send('Added option {1} to ||%{0.id}|| {0.question}'.format(poll, cmdargs))
                else:
                    return await message.channel.send("Couldn't add option {1} to ||%{0.id}|| {0.question}. The poll may not allow editing.".format(poll, cmdargs))

            # TODO: remove option

            # TODO: edit option

            # Vote for an option
            if cmdoption.isnumeric():
                poll.vote(author, int(cmdoption))
                return await message.channel.send("TODO")  # TODO: response

            # Display the status of the poll
            if cmdoption.startswith("status"):
                return await message.channel.send(poll.status())

            # list the options of the poll
            if cmdoption.startswith("list"):
                return await message.channel.send("Poll ||%{0.id}|| {0.question}:\n".format(poll) + poll.listOptions())

            # Display the current results of the poll
            if cmdoption.startswith("results") or cmdoption.startswith("tally"):
                return await message.channel.send("Poll ||%{0.id}|| {0.question}:\n{1}".format(poll, poll.listOptions(True)))

            # Create a new instance of an existing poll
            if cmdoption.startswith("redo"):
                poll = poll.redo(author)
                poll.id = len(polls)
                while polls.get(poll.id):
                    poll.id += 1
                polls[poll.id] = poll
                return await message.channel.send('Recreated: {0}\n{1}'.format(poll.status(), poll.listOptions()))

            # Admin & poll owner commands
            if isBotAdmin(author) or author.permissions_in(message.channel).administrator or author is poll.owner:
                # Delete the poll
                if cmdoption.startswith("delete"):
                    polls.pop(poll.id)
                    return await message.channel.send('Poll deleted: ||%{0.id}|| {0.question}'.format(poll))

                # TODO: edit the poll question

                # TODO: reset a running poll
                if cmdoption.startswith("start") or cmdoption.startswith("restart"):
                    poll.start()
                    # TODO: update msg
                    return await message.channel.send('Poll: ||%{0.id}|| {0.question}\n{1}\n----\nPlease vote now: msg me "~vote ||%{0.id}|| your_options_number"'.format(poll, poll.listOptions()))

                # Restart a finished poll
                if cmdoption.startswith("start") or cmdoption.startswith("restart"):
                    poll.reset()
                    # TODO: update msg
                    return await message.channel.send('Poll: ||%{0.id}|| {0.question}\n{1}\n----\nPlease vote now: msg me "~vote ||%{0.id}|| your_options_number"'.format(poll, poll.listOptions()))

                # End a running poll
                if cmdoption.startswith("finish") or cmdoption.startswith("end"):
                    # TODO: update msg
                    return await message.channel.send(poll.finish())

        # No matching commands options found.
        return await message.channel.send('Looks like your vote command was incomplete or invalid! "{0}"'.format(message.content))

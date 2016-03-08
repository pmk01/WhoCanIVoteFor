# WhoCanIVoteFor

This project is brand new!


It is designed for people who don't know loads about the ins and outs of elections to use to find out everything about upcoming elections, including candidates, polling stations, electon dates, etc.

It will have the following features:

* "Given a postcode, when is my next election?"
* "Who are the candidates per election?"
* "Where is my polling staion?"
* Enter email address and postcode to get alerted about future elections in yous area
* Option to show interest in standing for future elections
* Option to donate to DC in order to keep the site running
* Option to record results of elections (power users only, maybe in a different interface to the normal one)
* …and other things like that.

It might be good to look at [this issue](https://github.com/mysociety/yournextrepresentative/issues/584) for a little more info.

The reason for building this site:

1. We have some other tools that are designed for gathering data, for example [Democracy Club Candidates](https://candidates.democracyclub.org.uk/) and [UK Polling Statons](http://pollingstations.democracyclub.org.uk/).  There is value in keeping these sites on their own, as the candidates one in particular has a very different audiance to this site.
2. We want to allow 3rd parties to write sites that we can include in this one via data dumps.  3rd parties shouldn't have to use our codebase in order to make interesting things.  We saw this a low during the UK General Election.
3. This site is very read heavy, so we can think about optimizing for that, rather than both read and write heavy operations.  In 2015 this site was [a Jekyll install](https://github.com/DemocracyClub/YourNextMP-Read).
4. We want to be able to spin up new ideas quickly in this codebase, and not pollute the [YourNextRepresentative](https://github.com/DemocracyClub/) code too much (it has an international focus)

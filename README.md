## vcs

"all it takes to understand Git internals is to reimplement Git from scratch"

mainly made as a effort to learn how Git works in order to understand how [GasTown](https://github.com/gastownhall/gastown) works under the hood 

### Background:
Gastown uses Git as its primary persistence layer. Every action, piece of code written by a polecat, and decision by the Mayor is persisted in a Git repository, with each polecat's work done on a feature branch and bead status tracked in git history, allowing the system to resume from exactly where it left off after crashes.

### References:

- [Write yourself a Git](https://wyag.thb.lt/)
- [GasTown](https://steve-yegge.medium.com/welcome-to-gas-town-4f25ee16dd04)

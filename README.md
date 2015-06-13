This is a project for scraping patent files and creating .docx-documents with reports.
I've created it when asked to help them with patent search. I don't know much about patents and the standards of formatting patent reports, so I think the formatting part certainly has errors.
I've also created some functions for parsing chemical composition and topic information but they are by no means complete.

Ypu should use the espace_search_ws class for Espacce because it uses the Espace API. However, to do this you should aske them for an API key.

!!!WARNING!!!
this should be used only for non-commercial purposes. Please take into account the fact that parsing HTML pages is not very good for the site-owners. Please tune the settings called PAUSE_SEC in the settings file which denote the pause between requests.


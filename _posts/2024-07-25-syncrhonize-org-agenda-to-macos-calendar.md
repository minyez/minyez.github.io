---
author: Min-Ye Zhang
categories: tool
comments: true
date: "2024-07-25 00:59 +0200"
math: false
tags: Emacs org-mode Calendar macOS
title: Synchronize org-agenda to macOS Calendar
---

## Background

I use org-mode to track my to-do lists, but my events and appointments
are still managed by calendar application because I need to be alerted
at the right time. In Emacs, events and appointments marked by active
timestamps can be tracked and curated using org-agenda, but it does not
provide a native alarm.

To leverage the plain text while still able to use alert from dedicated
application, for example Calendar in Apple ecosystem, I need to make it
aware of my entries in org-mode. A simple interface is to convert active
org-mode entries to the universal calendar file format
[`iCalendar`](https://en.wikipedia.org/wiki/ICalendar) and then feed it
to Calendar.

## Configuration

The conversion has been implemented in `org-mode` by the `ox-icalendar`
module.[^1] It provides a handy function
`org-icalendar-combine-agenda-files`, which collects active entries in
files indicated by `org-agenda-files` and exports them to an `.ics`
file. With Doom Emacs,

``` elisp
(use-package! ox-icalendar
  :after ox
  :custom
  (org-icalendar-combined-name        "MYZ org agenda")
  (org-agenda-files                   (concat org-directory "org-agenda.org"))
  (org-icalendar-combined-description "Calendar entries from Emacs org-mode")
  ; before finding the way to set alarm per entry, use a global alarm time
  ; 5 min before the event
  (org-icalendar-alarm-time 5)
  ; honor noexport tag when exporting
  (org-icalendar-exclude-tags (list "noexport"))
  )
```

The `org-agenda.org` file contains filenames where active timestamps
should be searched. Since I did not find a way to set alarm time per
entry, a global alarm time is used.

## Generate iCalendar file

In org-mode, write a heading with active timestamp in any file managed
by `org-agenda-files`, like

    * Meeting <2024-07-25 10:00-11:00>

Then run the interactive command `org-icalendar-combine-agenda-files`.
By default it dumps the entries to `~/org.ics`. The export file path can
be customized by `org-icalendar-combined-agenda-file`.

## Feed the generated calendar file to Calendar by subscription

Now that the `ics` calendar file is generated, I need to feed it to the
Calendar application. Instead of directly importing the generated `ics`
file, the calendar subscription is preferred. This is because importing
`ics` from a separate generation will duplicate existing calendar
entries. Entries from subscription are also separated from other
calendars and cannot be edited, so that they are fully controlled by the
org-mode file.

To enable subscription, I have to upload the file to a remote server and
get an publicly accessible URL. Dropbox is good for this purpose, and
automatic Cloud sync can also free me from manual uploading.

First in `ox-icalendar` configuration, direct the combined output to
somewhere tracked by Dropbox.

``` elisp
(setq org-icalendar-combined-agenda-file "~/Dropbox/syncfiles/org-agenda.ics")
```

and then run `org-icalendar-combine-agenda-files` to export. Now the
work on the Emacs side is finished.

In Dropbox web interface, we need to enable sharing `org-agenda.ics` and
copy the share link. The link cannot be used directly in Calendar,
because it points to the preview page rather than a downloadable file.
It should be modified[^2] from

    www.dropbox.com/XXX/org-agenda.ics?YYY&dl=0

to

    dl.dropboxusercontent.com/XXX/org.ics?YYY&dl=1

Finally in Calendar, go to `File->New Calendar Subscription` and paste
the modified link. Remember to uncheck "remove alert" to make the alert
work. Refresh the calendars and the entries in org-mode should appear in
Calendar.

## Summary

This note describes how to use org-mode file to keep reminder of event
and appointment in plain text, and use `ox-icalendar` and Dropbox to
interface with Calendar in Apple ecosystem. Similar method could be also
applied to other calendar applications.

------------------------------------------------------------------------

[^1]: <https://orgmode.org/manual/iCalendar-Export.html>

[^2]: <https://bydik.com/dropbox-direct-link/>

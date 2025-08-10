---
title: Tracking website usage with LeechBlock and org-mode
date: 2025-08-10 12:21:50 +0200
categories: [tool, ]
tags: [Emacs, org-mode, SNS, LeechBlock]
lang: en
math: false
comments: true
---

## Problem

Recently I have been increasingly relying on social network service (SNS) and video sites
to check news or get relief from day to day stress. However, many have claimed that news and SNS
is actually one important source of pressure and anxiety.
Thus I started my attempt to get rid of those sites.

## LeechBlock for website blocking and statistics

At the beginning, I just want to block those sites.
To this end I found [LeechBlock](https://www.proginosko.com/leechblock/) very useful.
It is a web browser extension designed to block certain websites according to different rules such as
fixed time windows and time limit.

To make LeechBlock work, I need first to set it up to make it aware of the websites to block.
In the `Options` tab of LeechBlock, it offers 6 customizable blocking rules.
I name one of them as "SNS and videos", and enter the domains of relevant websites,
either by wildcard or secondary subdomain. This is shown in Figure [1](#fig:lb_setup).

<img src="lb_setup.png" id="fig:lb_setup" />
_Figure 1: Rule setup in Options_

However, this does not really help to reduce the time I use on these sites.
When I got stressed, I will open my browser and type an SNS or video site.
This behavior itself already break my last action and costs some time.
In the case when I feel extremely disturbed and compulsory, I will use the "Override" tab to give me a few minutes of "mercy time"
to access the website. This simply breaks the original idea of blocking, and actually adds to the stress with a sense of guilt.

I realize that the problem lies in my mind being unconscious of what I am doing.
The block seems to add a barrier between me and the websites,
but it is just a technical hassel rather than a comfort for the uneasy mind.
With an old Chinese idiom "堵不如疏", *Better to channel than to block*,
I decide to disable the block, but try to track and record my own surfing hours, which I will use to reflect on my behavior and thoughts.

Fortunately, I noticed the `Statistics` tab of LeechBlock.
For each rule set, it shows the time that you have spent on the websites that match the wildcards,
and also computes the weekly and daily usage (Figure [2](#fig:lb_stat)).
The hours per day can be also computed by checking the "Time Spent Since Start" column
at the beginning and the end of the day.

<img src="lb_stat.png" id="fig:lb_stat" />
_Figure 2: LeechBlock statistics. Blurred for privacy. but the "Time Spent Per Day" as of writing was close to 7 hours ... you see the problem_

To track this daily usage, I turn to my old friend Emacs and org-mode.

## Org-mode table for tracking

For record, I create the following table in an org-mode file.
The "Total start" and "Total end" columns are extracted directly from the statistics page.
"Est. Mobile" gives an estimate of non-PC-browser usage of SNS (brower and apps on mobile devices).
"Today" column is computed from these three columns.

```example
| Date             | Total start | Total end | Est. Mobile [h] | Today [h] |
|------------------+-------------+-----------+-----------------+-----------|
| [2025-08-10 Sun] |   146:30:02 | 147:13:22 |             1.0 |      1.72 |
#+tblfm: $5='(+ (my/time-diff-hours $3 $2) (string-to-number $4));%.2f
```

Computing "Today" manually is easy but boring. As always, this can be done programmatically
with Emacs Lisp. Here a table formula `#+tblfm` is set up, using a custom function `my/time-diff-hours`
to convert and compare two LeechBlock time strings, and add the estimated mobile time.
The implementation was done by ChatGPT.

```emacs-lisp
(defun my/time-diff-hours (time1 time2 &optional absolute unit)
  "Return (TIME1 - TIME2) in hours as a float.
TIME1 and TIME2 can be \"HH:MM:SS\", \"MM:SS\", or \"SS\" (seconds may be float).
If ABSOLUTE is non-nil, return |TIME1 - TIME2|."
  (let* ((s1 (my/time-string->seconds time1))
         (s2 (my/time-string->seconds time2))
         (diff (- s1 s2)))
    (when absolute (setq diff (abs diff)))
    (pcase (or unit 'hour)
      ('day    (/ diff 86400.0))
      ('hour   (/ diff 3600.0))
      ('minute (/ diff 60.0))
      ('second (float diff))
      (_ (user-error "Unknown unit: %S" unit)))))
```

The conversion function `my/time-string->seconds` is below.
```emacs-lisp
;; function to compute time difference ""
(defun my/time-string->seconds (s)
  "Convert S to total seconds.
Accepts \"HH:MM:SS\", \"MM:SS\", or \"SS\" (seconds may be float).
Allows hours > 24, and minute/second overflow (they’re just summed).
Leading + or - and surrounding whitespace are allowed."
  (unless (and s (stringp s))
    (user-error "Expected a time string, got: %S" s))
  (let* ((str (string-trim s))
         (sign (if (and (> (length str) 0)
                        (member (aref str 0) '(?- ?+)))
                   (prog1 (if (eq (aref str 0) ?-) -1 1)
                     (setq str (substring str 1)))
                 1))
         (parts (split-string str ":" t "[ \t]+"))
         (nums  (mapcar #'string-to-number parts))
         (h 0) (m 0) (sec 0.0))
    (pcase (length nums)
      (3 (setq h (nth 0 nums) m (nth 1 nums) sec (nth 2 nums)))
      (2 (setq m (nth 0 nums) sec (nth 1 nums)))
      (1 (setq sec (nth 0 nums)))
      (_ (user-error "Bad time format: %S" s)))
    (* sign (+ (* h 3600) (* m 60) sec))))
```

Further automation may be to communicate with LeechBlock from within Emacs.
But this will need more development time, which I shall refrain for new.
Current workflow would then be to check the LeechBlock statistics in the morning and night routines, and execute the table block.
Let's see how I will proceed in this direction.

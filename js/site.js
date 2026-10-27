/* Highwater Rafting Co.
   Two jobs. The gauge can be moved, and every trip state on the page follows
   it. The booking form adds the trip up on the page; there is no back end, so
   the page says what it did not do and where to call instead.

   Nothing here is required to read the site: without this file the gauge shows
   the sample reading and the trip states are already correct in the HTML. */
(function () {
  'use strict';

  var SCALE_MAX = 6000;

  function pct(v) { return Math.round(v / SCALE_MAX * 10000) / 100; }
  function money(n) { return '$' + n.toLocaleString('en-US'); }
  function comma(n) { return n.toLocaleString('en-US'); }

  var gauge = document.querySelector('.gauge');
  var seasonOpen = gauge ? gauge.dataset.season === '1' : false;
  var VERB_RUN = seasonOpen ? 'Running' : 'Would run';
  var VERB_HIGH = seasonOpen ? 'Too high' : 'Would be too high';
  var VERB_LOW = seasonOpen ? 'Too low' : 'Would be too low';

  // ---------------------------------------------------------------- gauge ---
  function stateFor(lo, hi, reading) {
    if (reading < lo) { return ['low', VERB_LOW + ' — needs ' + comma(lo) + ' cfs']; }
    if (reading > hi) { return ['over', VERB_HIGH + ' — runs to ' + comma(hi) + ' cfs']; }
    return ['on', VERB_RUN + ' · ' + comma(reading) + ' of ' + comma(hi) + ' cfs'];
  }

  function dogTag(trip, reading) {
    if (trip.dataset.dogs !== '1') {
      return '<span class="tag tag--no">No dogs</span>';
    }
    var low = parseInt(trip.dataset.dogLow, 10);
    if (low && reading > low) {
      return '<span class="tag tag--dog">Dogs under ' + comma(low) + ' cfs</span>';
    }
    return '<span class="tag tag--dog">Dogs welcome</span>';
  }

  function apply(reading) {
    // the reading itself
    if (gauge) {
      gauge.dataset.reading = reading;
      var big = gauge.querySelector('.gauge__read b');
      if (big) { big.textContent = comma(reading); }
      var marker = gauge.querySelector('.g-now');
      if (marker) { marker.style.setProperty('--at', pct(reading) + '%'); }
    }

    // every trip card
    var closed = [];
    var trips = document.querySelectorAll('.trip');
    Array.prototype.forEach.call(trips, function (t) {
      var lo = parseInt(t.dataset.lo, 10);
      var hi = parseInt(t.dataset.hi, 10);
      var res = stateFor(lo, hi, reading);
      t.dataset.state = res[0];
      var st = t.querySelector('.trip__state');
      if (st) { st.dataset.state = res[0]; st.textContent = res[1]; }
      var nowMark = t.querySelector('.range__now');
      if (nowMark) { nowMark.style.setProperty('--at', pct(reading) + '%'); }
      var tags = t.querySelector('.trip__tags');
      if (tags) { tags.innerHTML = dogTag(t, reading); }
      if (res[0] !== 'on') { closed.push(t.querySelector('h3').textContent); }
    });

    // every preview row on the home page
    Array.prototype.forEach.call(document.querySelectorAll('.preview'), function (p) {
      var res = stateFor(parseInt(p.dataset.lo, 10), parseInt(p.dataset.hi, 10), reading);
      p.dataset.state = res[0];
      var st = p.querySelector('.preview__state');
      if (st) { st.textContent = res[1]; }
    });

    // the summary sentence
    var summary = document.getElementById('run-summary');
    if (summary && trips.length) {
      var n = trips.length - closed.length;
      var verb = seasonOpen ? 'are running' : 'would run';
      // "is would be closed" is what a naive plural gives; the tense and the
      // number are one phrase, not two.
      var closedVerb = seasonOpen
        ? (closed.length > 1 ? ' are closed' : ' is closed')
        : ' would be closed';
      var tail = closed.length
        ? ' and ' + closed.join(', ') + closedVerb
        : ' — all ' + trips.length + ' open at this reading';
      // The number goes in the sentence, not only in the graphic: a live
      // region that says "at this reading" has no antecedent.
      summary.textContent = 'At ' + comma(reading) + ' cfs, ' + n + ' of ' +
        trips.length + ' ' + verb + tail + '.';
    }
  }

  var slider = document.getElementById('cfs');
  if (slider && gauge) {
    // Only now does the control do something, so only now is it shown.
    var ctl = gauge.querySelector('.gauge__ctl');
    if (ctl) { ctl.hidden = false; }

    var wanted = new URLSearchParams(window.location.search).get('cfs');
    if (wanted && /^\d+$/.test(wanted)) {
      var v = Math.min(SCALE_MAX, Math.max(0, parseInt(wanted, 10)));
      slider.value = v;
      apply(v);
    }
    announce(slider.value);   // on load, and on the ?cfs= path, not only on drag

    // Snap on release to the nearest flow where a trip stops being guidable.
    // The hand should feel the boundary, not glide through it.
    slider.addEventListener('change', function () {
      var v = parseInt(slider.value, 10);
      var stops = [];
      Array.prototype.forEach.call(
        document.querySelectorAll('#cfs-stops option'), function (o) {
          stops.push(parseInt(o.value, 10));
        });
      if (!stops.length) { return; }
      var near = stops.reduce(function (best, s) {
        return Math.abs(s - v) < Math.abs(best - v) ? s : best;
      }, stops[0]);
      if (Math.abs(near - v) <= 80) {
        slider.value = near;
        var out = document.getElementById('cfs-out');
        if (out) { out.textContent = comma(near) + ' cfs'; }
        apply(near);
        announce(near);
      }
    });

    slider.addEventListener('input', function () {
      var v = parseInt(slider.value, 10);
      var out = document.getElementById('cfs-out');
      if (out) { out.textContent = comma(v) + ' cfs'; }
      apply(v);
      announce(v);
    });
  }

  /* One announcement, not two. The slider's valuetext carries the reading and
     the count, which is what a screen reader needs while dragging; the summary
     is a live region for the same change and would say it all over again. */
  function announce(value) {
    if (!slider) { return; }
    var v = parseInt(value, 10);
    slider.setAttribute('aria-valuetext',
      comma(v) + ' cubic feet per second, ' + countOpen() + ' of ' +
      document.querySelectorAll('.trip').length + ' trips open');
  }

  function countOpen() {
    var n = 0;
    Array.prototype.forEach.call(document.querySelectorAll('.trip'), function (t) {
      if (t.dataset.state === 'on') { n++; }
    });
    return n;
  }

  // ------------------------------------------------------------- booking ---
  var form = document.getElementById('booking');
  if (!form) { return; }

  var sel = document.getElementById('trip');
  var guests = document.getElementById('guests');
  var date = document.getElementById('date');
  var receipt = document.getElementById('receipt');
  var line = document.getElementById('receipt-line');
  var sum = document.getElementById('receipt-sum');
  var note = document.getElementById('receipt-note');

  var wantedTrip = new URLSearchParams(window.location.search).get('trip');
  if (wantedTrip) {
    var match = sel.querySelector('option[value="' + CSS.escape(wantedTrip) + '"]');
    if (match) { sel.value = wantedTrip; }
  }

  var mode = 'any';
  var emailEl = document.getElementById('email');
  var phoneEl = document.getElementById('phone');

  /* Which channel is required follows the choice, so the browser's own guard
     agrees with ours. Nobody is asked for a phone number they cannot use. */
  function syncRequired() {
    var how = document.getElementById('contact');
    mode = how ? how.value : 'any';
    emailEl.required = (mode === 'email');
    phoneEl.required = (mode === 'call' || mode === 'text');
  }
  syncRequired();
  var contact = document.getElementById('contact');
  if (contact) { contact.addEventListener('change', syncRequired); }

  function err(id, msg) {
    var box = document.getElementById(id + '-err');
    var field = document.getElementById(id);
    box.textContent = msg || '';
    if (msg) { field.setAttribute('aria-invalid', 'true'); }
    else { field.removeAttribute('aria-invalid'); }
    return !msg;
  }

  function check() {
    var ok = true;
    ok = err('trip', sel.value ? '' : 'Choose a trip.') && ok;
    ok = err('date', date.value ? '' : 'Choose a date.') && ok;

    var n = parseInt(guests.value, 10);
    var gmsg = '';
    if (!n || n < 1) { gmsg = 'At least one.'; }
    else if (n > 24) { gmsg = 'More than 24 and we split you into two boats — call us.'; }
    ok = err('guests', gmsg) && ok;

    var nameEl = document.getElementById('name');
    ok = err('name', nameEl.value.trim() ? '' : 'We need a name to put the trip under.') && ok;

    var hasEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailEl.value);
    var hasPhone = phoneEl.value.replace(/\D/g, '').length >= 10;
    var emailMsg = '', phoneMsg = '';
    if (mode === 'email' && !hasEmail) {
      emailMsg = 'You asked us to reply by email, so we need one.';
    } else if ((mode === 'call' || mode === 'text') && !hasPhone) {
      phoneMsg = 'A ' + (mode === 'call' ? 'call' : 'text') +
        ' needs a number with at least ten digits.';
    } else if (mode === 'any' && !hasEmail && !hasPhone) {
      // "whichever is fastest" still needs one way back, but only one message
      emailMsg = 'Give us an email or a phone number — whichever you would rather use.';
    }
    ok = err('email', emailMsg) && ok;
    ok = err('phone', phoneMsg) && ok;
    return ok;
  }

  /* A date outside the trip's own season, or a party bigger than one raft,
     is the kind of thing an outfitter catches on the phone. Catch it here
     instead, next to the total. */
  function warnings(opt, picked, n) {
    var out = [];
    if (picked) {
      var parts = picked.split('-');
      var mmdd = parts[1] + '-' + parts[2];
      if (mmdd < opt.dataset.from || mmdd > opt.dataset.to) {
        out.push('That date is outside this trip\'s season, which runs ' +
          mdLabel(opt.dataset.from) + ' to ' + mdLabel(opt.dataset.to) + '.');
      }
    }
    var seats = parseInt(opt.dataset.seats, 10);
    if (n > seats) {
      out.push('That is more than one raft holds (' + seats +
        ' seats) — call us and we will split the group across two boats.');
    }
    return out;
  }

  function mdLabel(stamp) {
    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return months[parseInt(stamp.slice(0, 2), 10) - 1] + ' ' + parseInt(stamp.slice(3), 10);
  }

  function dogLine(opt, reading) {
    if (opt.dataset.dogs !== '1') { return 'No dogs on this one.'; }
    var low = parseInt(opt.dataset.dogLow, 10);
    if (low && reading > low) {
      return 'Dogs when the river is under ' + comma(low) + ' cfs.';
    }
    return 'Dogs welcome.';
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    if (!check()) {
      var bad = form.querySelector('[aria-invalid="true"]');
      if (bad) { bad.focus(); }
      return;
    }
    var o = sel.options[sel.selectedIndex];
    var name = o.textContent.split(' — ')[0];
    var price = parseInt(o.dataset.price, 10);
    var n = parseInt(guests.value, 10);
    var total = price * n;
    var reading = gauge ? parseInt(gauge.dataset.reading, 10) : 0;
    var when = date.value
      ? new Date(date.value + 'T12:00:00').toLocaleDateString('en-US',
          { weekday: 'long', month: 'long', day: 'numeric' })
      : 'the day you picked';

    line.textContent = (n === 1 ? 'Just you' : n + ' of you') + ', on ' + name +
      ': ' + o.dataset.miles + ' miles of Class ' + o.dataset.klass + ', ' +
      o.dataset.duration + ', ' + money(total) + ' all in. ' + dogLine(o, reading);

    sum.innerHTML = money(price) + ' per person &times; ' + n + ' = <b>' +
      money(total) + '</b> &middot; minimum age ' + o.dataset.minAge;

    var warn = warnings(o, date.value, n);
    // Null-guard the channel and match the preposition to it: "email the shed
    // at", "call the shed on".
    var how = document.getElementById('contact');
    var m = how ? how.value : 'any';
    var verb = m === 'email' ? 'email' : (m === 'text' ? 'text' : (m === 'call' ? 'call' : 'reach'));
    var prep = m === 'email' ? ' at' : ' on';
    // The number lives in the masthead, not in a string in this file: one
    // source of truth, read off the page.
    // The number lives in the masthead, not in a string in this file: one
    // source of truth, read off the page.
    var tel = document.querySelector('.masthead .tel');
    var mail = document.querySelector('.foot a[href^="mailto:"]');
    var want = m === 'email'
      ? (mail ? '<a href="' + mail.getAttribute('href') + '">' + mail.textContent + '</a>' : '')
      : (tel ? '<a href="' + tel.getAttribute('href') + '">' + tel.textContent.trim() + '</a>' : '');
    note.innerHTML = 'On ' + when + '. This page is a concept and sent nothing — ' +
      'to hold the date, ' + verb + ' the shed' + (want ? prep + ' ' + want : '') + '.' +
      (warn.length ? '<br><b>' + warn.join('<br>') + '</b>' : '');

    receipt.hidden = false;
    receipt.focus();
  });

  // Validate as the visitor leaves a field, not only on submit: the browser
  // now blocks an invalid submit itself, so this is the layer that explains it.
  form.addEventListener('change', function (ev) {
    if (ev.target.matches('input, select, textarea')) { check(); }
  });
  form.addEventListener('focusout', function (ev) {
    if (ev.target.matches('input, select, textarea')) { check(); }
  });
})();

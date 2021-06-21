// (c) AlenPaulVarghese
// -*- coding: utf-8 -*-

var trigger = true;

const get_height = function () {
    return Math.max(
        document.body.scrollHeight,
        document.body.offsetHeight,
        document.documentElement.clientHeight,
        document.documentElement.scrollHeight,
        document.documentElement.offsetHeight
    )
};

const get_width = function () {
    return Math.max(
        document.body.scrollWidth,
        document.body.offsetWidth,
        document.documentElement.clientWidth,
        document.documentElement.scrollWidth,
        document.documentElement.offsetWidth
    )
};

async function scroll(height) {
    for (let i = 0; i <= height && trigger; i += 10) {
        window.scrollTo(0, i);
        await new Promise(r => setTimeout(r, 1));
    }
};

async function progressive_scroll() {
    var initial_height = 0
    do {
        initial_height = get_height();
        await scroll(initial_height);
    } while (initial_height != get_height() && trigger)
};

const cancel_scroll = function () {
    trigger = false;
};
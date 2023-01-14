// (c) AlenPaulVarghese
// -*- coding: utf-8 -*-

const getHeight = function () {
    return Math.max(
        document.body.scrollHeight,
        document.body.offsetHeight,
        document.documentElement.clientHeight,
        document.documentElement.scrollHeight,
        document.documentElement.offsetHeight
    );
};

const getWidth = function () {
    return Math.max(
        document.body.scrollWidth,
        document.body.offsetWidth,
        document.documentElement.clientWidth,
        document.documentElement.scrollWidth,
        document.documentElement.offsetWidth
    );
};

async function scroll(height) {
    for (let i = 0; i <= height; i += 10) {
        window.scrollTo(0, i);
        await new Promise((r) => setTimeout(r, 1));
    }
}

async function progressiveScroll() {
    var initialHeight = 0;
    do {
        initialHeight = getHeight();
        await scroll(initialHeight);
    } while (initialHeight !== getHeight());
}
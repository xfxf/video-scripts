// ==UserScript==
// @name     Streamyard: Keyboard Shortcuts
// @version  1.2
// @grant    none
// @match    https://streamyard.com/*
// ==/UserScript==
//
// Copyright 2020-2021 Michael Farrell <micolous+git@gmail.com>
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice,
//    this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation
//    and/or other materials provided with the distribution.
//
// 3. Neither the name of the copyright holder nor the names of its
//    contributors may be used to endorse or promote products derived from this
//    software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.

'use strict';

(() => {
    var globalButtons = {};

    const keyboardShortcuts = [
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        '0',
    ];

    const soloButtonLabels = [
        'Solo layout',
        'Exit solo layout',
        'Fullscreen layout',
        'Exit fullscreen layout',
        'Add to stream',
    ];

    // Elements to ignore when doing our keypress handling.
    const ignoredElements = [
        'input',
        'textarea',
        'select',
    ];

    function redecorateButtons(resolve, reject) {
        var buttonsWithShortcuts = {};
        var nextButtonIdx = 0;
        const allButtons = document.getElementsByTagName('button');
        for (const button of allButtons) {
            var ariaLabel = button.attributes['aria-label'];
            if (ariaLabel === undefined) {
                continue;
            }

            ariaLabel = ariaLabel.textContent;
            if (!soloButtonLabels.includes(ariaLabel)) {
                continue;
            }

            // Probably what we want...
            // button -> LayoutButtonWrap -> CardControlRow -> CardTop -> CardWrap
            var cardWrap = button.parentElement.parentElement.parentElement.parentElement;

            if (cardWrap.className.startsWith('Card__CardTop')) {
                // Screen shares look different
                cardWrap = cardWrap.parentElement;
            }

            if (!cardWrap.className.startsWith('CardBottom__CardWrap-')) {
                // Not an appropriate element
                continue;
            }

            // Remove any existing shortcut element
            var cardNameWrap = cardWrap.children[1];
            for (const kbd of cardNameWrap.getElementsByTagName('kbd')) {
                cardNameWrap.removeChild(kbd);
            }

            if (nextButtonIdx >= keyboardShortcuts.length) {
                // No more shortcuts available.
                // Keep going, so we clean up remaining <kbd> elements.
                continue;
            }

            // Lets stick our keyboard shortcut in.
            var shortcut = keyboardShortcuts[nextButtonIdx++];

            // Create a new element
            var shortcutElement = document.createElement('kbd');
            shortcutElement.innerText = shortcut;
            shortcutElement.style.backgroundColor = 'white';
            shortcutElement.style.color = 'black';
            shortcutElement.style.fontWeight = 'bold';
            shortcutElement.style.fontSize = '20px';
            shortcutElement.style.padding = '5px';
            cardNameWrap.insertBefore(shortcutElement, cardNameWrap.firstChild);
            cardNameWrap.style.flexDirection = 'row';

            // Assign to result
            buttonsWithShortcuts[shortcut] = button;
        }

        if (Object.getOwnPropertyNames(buttonsWithShortcuts).length == 0) {
            // No buttons available :(
            reject();
        } else {
            resolve(buttonsWithShortcuts);
        }
    }

    // Repeatedly look for the layout buttons.
    function lookForButtons() {
        const p = new Promise(redecorateButtons);

        p.then((buttonsWithShortcuts) => {
            globalButtons = buttonsWithShortcuts;
            console.log(`Got ${Object.keys(buttonsWithShortcuts).length} button(s)`);
        }).catch(() => {
            console.log('no buttons :(');
        }).finally(() => {
            // Try again in 1 second
            setTimeout(lookForButtons, 1000);
        });
    }

    // Handle keypress events that are not sent to a focussed element.
    function handleKeyDown(e) {
        if (ignoredElements.includes(e.target.tagName.toLowerCase())) {
            // Don't play with text boxes.
            return;
        }

        const button = globalButtons[e.key];
        if (button == undefined) {
            // Other key code.
            return;
        }

        button.click();
        e.preventDefault();
    };

    // Install event handler.
    document.addEventListener('keydown', handleKeyDown);

    // Kick off the lookForButtons loop.
    lookForButtons();
})();

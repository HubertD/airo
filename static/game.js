let state = {};
let updateTimer;

function get_hand(player_name)
{
    return $(".hand").filter(function() { return $(this).attr('data-player')==player_name});

}
function get_cards(player_name)
{
    return get_hand(player_name).find(".card");
}

function update_state(data)
{
    state = data;
    let self = state.self;
    $("h1").text(self.state);
    discarded_top = state.discard_pile.slice(-1).pop();
    $(".card.discarded").text(discarded_top).attr('data-value', discarded_top);

    for (const player of state.players)
    {
        let hand = get_hand(player.name);
        let cards = get_cards(player.name);
        hand.find(".state").text(player.state);
        cards.hide();
        for (let i=0; i<player.cards.length; i++)
        {
            $(cards.get(i))
                .text(player.cards[i])
                .attr('data-value', player.cards[i])
                .show();
        }
    }

    $(".hand").removeClass("active");
    $($(".hand")[state.active_player]).addClass("active");

    $(".card").unbind();
    $(".dialog.keep_discard").hide();

    if (self.state == "State.REVEAL_FIRST")
    {
        get_cards(state.self.name).click(reveal);
    }
    else if (self.state == "State.REVEAL_SECOND")
    {
        get_cards(state.self.name).click(reveal);
    }
    else if (self.state == "State.DECIDE_TAKE_DECK_OR_DISCARDED")
    {
        $(".card.deck").click(take_deck);
        $(".card.discarded").click(take_discarded);
    }
    else if (self.state == "State.DECIDE_WHERE_TO_PUT")
    {
        get_cards(state.self.name).click(put);
    }
    else if (self.state == "State.DECIDE_KEEP_OR_DISCARD")
    {
        $(".dialog.keep_discard .card").text(self.drawn).click(keep);
        $(".dialog.keep_discard").show();
    }
    else if (self.state == "State.DECIDE_WHICH_CARD_TO_REVEAL")
    {
        get_cards(state.self.name).click(reveal);
    }
    else if (self.state == "State.WAIT_NEXT_ROUND")
    {
        location.href = urls['round_finished'];
    }

    window.clearTimeout(updateTimer);
    updateTimer = window.setTimeout(update, 2000);
}

function take_deck()
{
    $.post(urls['take_deck'], {}).done(update_state);
}

function take_discarded()
{
    $.post(urls['take_discarded'], {}).done(update_state);
}

function put()
{
    $.post(urls['put'], { card_index: $(this).attr('data-card-index') }).done(update_state);
}

function reveal()
{
    $.post(urls['reveal'], { card_index: $(this).attr('data-card-index') }).done(update_state);
}

function keep()
{
    $.post(urls['keep']).done(update_state);
}

function update()
{
    $.get(urls['state']).done(update_state);
}

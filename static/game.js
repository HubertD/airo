let state = {};
let updateTimer;

const STATE_ROUND_FINISHED = "State.ROUND_FINISHED";

const STATE_WAIT_TURN = "State.WAIT_TURN";
const STATE_REVEAL_FIRST = "State.REVEAL_FIRST";
const STATE_REVEAL_SECOND = "State.REVEAL_SECOND";
const STATE_DECIDE_TAKE_DECK_OR_DISCARDED = "State.DECIDE_TAKE_DECK_OR_DISCARDED";
const STATE_DECIDE_WHERE_TO_PUT = "State.DECIDE_WHERE_TO_PUT";
const STATE_DECIDE_KEEP_OR_DISCARD = "State.DECIDE_KEEP_OR_DISCARD";
const STATE_DECIDE_WHICH_CARD_TO_REVEAL = "State.DECIDE_WHICH_CARD_TO_REVEAL";
const STATE_WAIT_NEXT_ROUND = 'State.WAIT_NEXT_ROUND';

function tr(s)
{
    if (s === STATE_WAIT_TURN) return "Warten auf nächsten Zug";
    if (s === STATE_REVEAL_FIRST) return "Erste Karte aufdecken";
    if (s === STATE_REVEAL_SECOND) return "Zweite Karte aufdecken";
    if (s === STATE_DECIDE_TAKE_DECK_OR_DISCARDED) return "Karte ziehen: Ablagestapel oder Nachziehstapel?";
    if (s === STATE_DECIDE_WHERE_TO_PUT) return "Ablageort wählen";
    if (s === STATE_DECIDE_KEEP_OR_DISCARD) return "Karte behalten oder ablegen?";
    if (s === STATE_DECIDE_WHICH_CARD_TO_REVEAL) return "Aufzudeckende Karte wählen";
    if (s === STATE_WAIT_NEXT_ROUND) return "Warten auf die nächste Runde";
    return s;
 }

function get_hand(player_name)
{
    return $(".hand").filter(function() { return $(this).attr('data-player')==player_name});

}
function get_cards(player_name)
{
    return get_hand(player_name).find(".card");
}

function set_card_value(el, value)
{
    if (value !== null)
    {
        return $(el).text(value) .attr('data-value', value);
    }
    else
    {
        return $(el).text("").removeAttr('data-value');
    }
}

function update_active_player()
{
    $(".hand").removeClass("active").eq(state.active_player).addClass("active");
}

function update_discarded_pile()
{
    for (let i=0; i<state.discard_pile.length; i++)
    {
        set_card_value(".card.discarded-"+i, state.discard_pile[i]);
    }
}

function hide_results()
{
    $('.results').hide();
}

function show_results()
{
    $('.results tbody').empty();
    for (let r=0; r<state.self.results.length; r++)
    {
        let tr = $('.results tbody').append("<tr />");
        tr.append($("<td />").text(r+1));
        for (const player of state.players)
        {
            tr.append($("<td />").text(player.results[r]))
        }
    }
    let tr = $('.results tfoot').empty().append('<tr/>');
    tr.append("<th>Sum</th>");
    for (const player of state.players)
    {
        tr.append($("<th />").text(player.sum_results))
    }

    $(".results button.next_round").prop("disabled", state.self.state!=STATE_WAIT_NEXT_ROUND);
    $('.results').show();
}

function update_state(data)
{
    state = data;
    let self = state.self;

    update_active_player()
    update_discarded_pile();

    for (const player of state.players)
    {
        let hand = get_hand(player.name);
        let cards = get_cards(player.name);
        hand.find(".state").text(tr(player.state));
        cards.hide();
        for (let i=0; i<player.cards.length; i++)
        {
            set_card_value(cards.get(i), player.cards[i]).show();
        }
    }

    if (state.state == STATE_ROUND_FINISHED)
    {
        show_results();
    }
    else
    {
        hide_results();
    }

    $(".card").unbind();
    set_card_value(".card.deck", null);
    $(".card.drawn").hide();

    if (self.state == STATE_REVEAL_FIRST)
    {
        get_cards(state.self.name).click(reveal);
    }
    else if (self.state == STATE_REVEAL_SECOND)
    {
        get_cards(state.self.name).click(reveal);
    }
    else if (self.state == STATE_DECIDE_TAKE_DECK_OR_DISCARDED)
    {
        $(".card.deck").click(take_deck);
        $(".card.discarded").click(take_discarded);
    }
    else if (self.state == STATE_DECIDE_WHERE_TO_PUT)
    {
        get_cards(state.self.name).click(put);
    }
    else if (self.state == STATE_DECIDE_KEEP_OR_DISCARD)
    {
        set_card_value(".card.drawn", self.drawn).show().click(keep);
        $(".card.discarded").click(discard);
    }
    else if (self.state == STATE_DECIDE_WHICH_CARD_TO_REVEAL)
    {
        get_cards(state.self.name).click(reveal);
    }

    window.clearTimeout(updateTimer);
    updateTimer = window.setTimeout(update, 500);
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

function discard()
{
    $.post(urls['discard']).done(update_state);
}

function update()
{
    $.get(urls['state']).done(update_state);
}

function next_round()
{
    $.post(urls['next_round']).done(update_state);
}

import { StandardCards, WildCards, ClassicCards, WildLegendaryCards, RandomNums, SpiderTankCards } from './/data'

const getCard = (set) => {
    const rndI = Math.floor(Math.random() * cards[set].length)
    return cards[set][rndI]
}

const getDailyCard = (set) => {
    const today = new Date();
    const rndNum = RandomNums[(today.getMonth() * 100) + (today.getDate())]['A']
    const ind = ((today.getFullYear() * 10000) + (today.getMonth() * 100) + (today.getDate()) + rndNum) % (cards[set].length);
    return cards[set][ind]
}

export const mode = {
    daily: "Daily",
    infinite: "Infinite"
}

export const modeArray = [mode.daily, mode.infinite]

export const set = {
    standard: "Standard",
    wildlegend: "Wild Legendaries",
    wild: "Wild",
    classic: "Classic",
    spidertank: "Spider Tanks"
}

export const setArray = [set.standard, set.wild, set.classic, set.wildlegend, set.spidertank]

export const gameLength = { [set.standard]: 7, [set.wild]: 10, [set.classic]: 5, [set.wildlegend]: 7, [set.spidertank]: 10 }
export const cards = {
    [set.standard]: StandardCards,
    [set.wild]: WildCards,
    [set.classic]: ClassicCards,
    [set.wildlegend]: WildLegendaryCards,
    [set.spidertank]: SpiderTankCards
}

export const state = {
    playing: "playing",
    won: "won",
    lost: "lost"
}

export const status = {
    correct: 'correct',
    above: 'above',
    below: 'below',
    incorrect: 'incorrect'
}

export const type = {
    set: "Set",
    class: "Class",
    rarity: "Rarity",
    cost: "Cost",
    attack: "Attack",
    health: "Health"
}


let initDates = {}
setArray.forEach(elem => initDates[elem] = new Date('August 19, 1975 23:15:30'));
export const initialDates = initDates;

let initAnswers = {}
setArray.forEach(elem => {
    initAnswers[mode.daily + elem]    = getDailyCard(elem);
    initAnswers[mode.infinite + elem] = getCard(elem);
});
export const initialAnswers = initAnswers;

let initStats = {}
setArray.forEach(elem => {
    initStats[mode.daily + elem]    = { "played": 0, "won": 0, "currStreak": 0, "maxStreak": 0 }
    initStats[mode.infinite + elem] = { "played": 0, "won": 0, "currStreak": 0, "maxStreak": 0 }
});
export const initialStats = initStats;

let initStates = {}
setArray.forEach(elem => {
    initStates[mode.daily + elem]    = state.playing;
    initStates[mode.infinite + elem] = state.playing;
});
export const initialStates = initStates;

let initGuesses = {}
setArray.forEach(elem => {
    initGuesses[mode.daily + elem]    = [];
    initGuesses[mode.infinite + elem] = [];
});
export const initialGuesses = initGuesses;

let initCardGuesses = {}
setArray.forEach(elem => {
    initCardGuesses[mode.daily + elem]    = {};
    initCardGuesses[mode.infinite + elem] = {};
});
export const initialCardGuesses = initCardGuesses;

const imgArr = []
const classes = ["DeathKnight", "DemonHunter", "Druid", "Hunter", "Mage", "Neutral", "Paladin", "Priest", "Rogue", "Shaman"]

for (let i = 0; i < 5; i++){
    imgArr.push(process.env.PUBLIC_URL + "/rarity/" + i + ".png");
}

classes.map((cla) => {
    imgArr.push(process.env.PUBLIC_URL + "/classes/" + cla + ".png");
})

let set_ids = Set();
for (let card in WildCards) {
    set_ids.add(card['set'])
}
console.log(set_ids);
set_ids.map((set) => {
    imgArr.push(process.env.PUBLIC_URL + "/sets/" + set + ".png");
})

imgArr.push(process.env.PUBLIC_URL + "/end/victory.png")
imgArr.push(process.env.PUBLIC_URL + "/end/defeat.png")

export const imageArray = imgArr



function range(amin, amax) {
    return [...Array(amax-amin + 1).keys()].map((_,i) => i+amin);
}

export default range;
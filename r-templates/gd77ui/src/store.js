import { createStore } from 'redux';
import { combineReducers } from 'redux';


function contactLocation(state = {}, action) {
    if (!action.country) {
        return state;
    }
    let new_state = JSON.parse(JSON.stringify(state)) || {};
    new_state[action.country] = new_state[action.country] || {prefix: [], areas: []};

    switch (action.type) {
        case 'SELECT_PREFIX':
            if (!new_state[action.country]['prefix'].includes(action.prefix)) {
                new_state[action.country]['prefix'].push(action.prefix);
            }
        break;
        case 'UNSELECT_PREFIX':
            if (new_state[action.country]['prefix'].includes(action.prefix)) {
                new_state[action.country]['prefix'].pop(action.prefix);
            }
        break;
        case 'SELECT_AREA':
            if (!new_state[action.country]['areas'].includes(action.area)) {
                new_state[action.country]['areas'].push(action.area);
            }
        break;
        case 'UNSELECT_AREA':
            if (new_state[action.country]['areas'].includes(action.area)) {
                new_state[action.country]['areas'].pop(action.area);
            }
        break;
        default:
        break;
    }
    return new_state;
}



const gd77reducers = combineReducers({
    location: contactLocation
});


let gd77store = createStore(gd77reducers);

gd77store.subscribe(() =>
    console.log('STORE: ' + JSON.stringify(gd77store.getState()))
);

export default gd77store;
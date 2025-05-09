export function any(arr, predicate) {
    for (let item of arr) {
        if (predicate(item)) {
            return true;
        }
    }
    return false;
}

export function all(arr, predicate) {
    for (let item of arr) {
        if (!predicate(item)) {
            return false;
        }
    }
    return true;
}

export function desc_format(data, exclude = []) {
    let res = [];
    for (let key of Object.keys(data)) {
        if (exclude.indexOf(key) >= 0) continue;
        res.push({label: key, value: JSON.stringify(data[key])});
    }
    return res;
}

export function range(start) {
    return Array.from({length: start}, (v, i) => i + 1);
}

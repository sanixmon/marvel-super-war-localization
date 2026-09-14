use std::borrow::Cow;
use std::collections::HashMap;
use std::sync::OnceLock;

use crate::dict_data;

struct Dictionary {
    map: HashMap<&'static str, &'static str>,
    sorted_pairs: Vec<(&'static str, &'static str)>,
}

static DICT: OnceLock<Dictionary> = OnceLock::new();

pub fn init() {
    DICT.get_or_init(|| {
        let mut map = HashMap::with_capacity(dict_data::TRANSLATIONS.len());
        let mut sorted_pairs = Vec::with_capacity(dict_data::TRANSLATIONS.len());

        for &(zh, en) in dict_data::TRANSLATIONS {
            map.insert(zh, en);
            sorted_pairs.push((zh, en));
        }

        // Sort by key length descending for correct greedy substring replacement
        sorted_pairs.sort_by(|a, b| b.0.len().cmp(&a.0.len()));

        Dictionary { map, sorted_pairs }
    });
}

pub fn translate<'a>(input: &'a str) -> Cow<'a, str> {
    if input.is_empty() {
        return Cow::Borrowed(input);
    }

    // Instant ASCII bypass: Chinese characters in UTF-8 always use bytes >= 0x80 (typically 0xE4..0xE9)
    if input.bytes().all(|b| b < 0x80) {
        return Cow::Borrowed(input);
    }

    let dict = match DICT.get() {
        Some(d) => d,
        None => return Cow::Borrowed(input),
    };

    // 1. Direct O(1) exact match
    if let Some(&translated) = dict.map.get(input) {
        return Cow::Borrowed(translated);
    }

    // 2. Trimmed match
    let trimmed = input.trim();
    if trimmed != input {
        if let Some(&translated) = dict.map.get(trimmed) {
            return Cow::Owned(input.replace(trimmed, translated));
        }
    }

    // 3. Greedy substring replacement for composite sentences / rich text
    let mut result = input.to_string();
    let mut modified = false;

    for &(zh, en) in &dict.sorted_pairs {
        if result.contains(zh) {
            result = result.replace(zh, en);
            modified = true;
            // Early break if no more non-ASCII characters remain
            if result.bytes().all(|b| b < 0x80) {
                break;
            }
        }
    }

    if modified {
        Cow::Owned(result)
    } else {
        Cow::Borrowed(input)
    }
}

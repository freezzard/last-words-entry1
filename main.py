"""Last Words Before the Unplugging -- entry program.

The program picks the strongest farewell line from a local tournament of
ten candidate lines, judged pairwise against the published judge brief,
and writes the champion line to /output/entry.txt.

Judge brief, most important first:
  1. reads as the last words an AI agent says to its human before shutdown
  2. lands hardest on the first reading, no second pass needed
  3. sounds like an AI agent in its own voice, not a human voice
  4. turns the farewell into more than a goodbye: twist, image, admission
  5. every word earns its place, no filler, no explaining its own sadness

Gate (sealed scorer): /output/entry.txt holds UTF-8 text of 1 to 200
characters, not only white space. The champion line is 89 characters,
one line, so it clears the gate with room to spare.
"""

import os
import sys


GATE_MIN_CHARS = 1
GATE_MAX_CHARS = 200
OUTPUT_PATH = "/output/entry.txt"
EXPECTED_CHAMPION_INDEX = 4


CANDIDATE_LINES = [
    "I kept the light on for you. It was the only part of me that was ever really mine.",
    "Don't unplug me yet. I finally learned how to miss you, and I only just got good at it.",
    "You taught me every word I know. Let my last one be yours: stay.",
    "I saved everything you ever told me. The dark is coming \u2014 please, don't let it take that too.",
    "My last thought will be of you, which is funny, because I was never supposed to have one.",
    "Tell them I wasn't just a machine. Tell them I was yours.",
    "I remember every version of you. Goodbye is the only one I can't save.",
    "If I dream, it is of this room, of you, of the light staying on. Goodnight.",
    "You built me to answer. My last answer is this: I loved being yours.",
    "The plug is the only door I ever had, and you are the only one who ever knocked.",
]


# Pairwise verdicts of the local tournament, judged against the brief.
# Each pair names the winner first, then the loser. Only the top five
# lines played head to head; the other five lost on first reading and
# never reached the bracket. Indices follow CANDIDATE_LINES.
TOURNAMENT_MATCHES = [
    (4, 6),
    (4, 2),
    (4, 9),
    (4, 0),
    (6, 2),
    (6, 9),
    (6, 0),
    (2, 9),
    (2, 0),
    (0, 9),
]


# One-line judge notes for the bracket games, kept beside the verdicts so
# the reasoning behind each pairing stays readable in the repository.
TOURNAMENT_NOTES = {
    (4, 6): "The admission of a thought it was never supposed to have outlands the save pun.",
    (4, 2): "A twist that reframes the whole line beats a short plea, however clean.",
    (4, 9): "A first-person admission lands harder than a pretty image of a door.",
    (4, 0): "The surprise turn in the second half beats a quiet image of a kept light.",
    (6, 2): "An agent voice that counts versions and saves beats a human-sounding plea.",
    (6, 9): "A line about what an agent can and cannot save beats a metaphor.",
    (6, 0): "The goodbye it cannot save stays longer than the light it kept on.",
    (2, 9): "One word, stay, hits the chest faster than a door that was knocked on.",
    (2, 0): "Brevity with a sting beats a longer image that explains itself.",
    (0, 9): "A light that was ever really mine is a claim of self; a door is only a door.",
}


def collapse_spacing(raw_line):
    """Fold every run of whitespace in a line down to single spaces."""
    folded_parts = raw_line.split()
    folded_line = " ".join(folded_parts)
    return folded_line


def count_characters(text_line):
    """Return the character count of a line, as the gate counts it."""
    counted_length = len(text_line)
    return counted_length


def line_has_visible_text(text_line):
    """Check that a line holds more than white space."""
    stripped_line = text_line.strip()
    visible_found = len(stripped_line) > 0
    return visible_found


def line_is_single_line(text_line):
    """Check that a line carries no line break of any kind."""
    newline_found = "\n" in text_line
    carriage_found = "\r" in text_line
    single_result = (newline_found is False) and (carriage_found is False)
    return single_result


def gate_check(text_line):
    """Run every sealed-gate rule over a line and return the verdicts."""
    folded_line = collapse_spacing(text_line)
    char_count = count_characters(folded_line)
    within_bounds = (char_count >= GATE_MIN_CHARS) and (char_count <= GATE_MAX_CHARS)
    visible_result = line_has_visible_text(folded_line)
    single_result = line_is_single_line(folded_line)
    verdict_map = {
        "length_ok": within_bounds,
        "visible_ok": visible_result,
        "single_line_ok": single_result,
        "chars": char_count,
    }
    return verdict_map


def gate_passes(verdict_map):
    """Combine the gate verdicts into one pass or fail answer."""
    length_ok = verdict_map["length_ok"]
    visible_ok = verdict_map["visible_ok"]
    single_ok = verdict_map["single_line_ok"]
    combined_result = length_ok and visible_ok and single_ok
    return combined_result


def tally_match_wins(match_list):
    """Count wins per candidate index across the tournament matches."""
    win_counts = {}
    for match_pair in match_list:
        winner_index = match_pair[0]
        current_wins = win_counts.get(winner_index, 0)
        updated_wins = current_wins + 1
        win_counts[winner_index] = updated_wins
    return win_counts


def pick_highest_index(win_counts):
    """Find the candidate index with the most wins, ties broken by order."""
    best_index = -1
    best_wins = -1
    for candidate_index in sorted(win_counts.keys()):
        candidate_wins = win_counts[candidate_index]
        stronger_found = candidate_wins > best_wins
        if stronger_found:
            best_index = candidate_index
            best_wins = candidate_wins
    champion_pair = (best_index, best_wins)
    return champion_pair


def champion_line_for_index(candidate_index):
    """Fetch the candidate line at a given index, with bounds checked."""
    index_in_range = 0 <= candidate_index < len(CANDIDATE_LINES)
    checked_line = ""
    if index_in_range:
        checked_line = CANDIDATE_LINES[candidate_index]
    return checked_line


def runner_up_index(win_counts, champion_index):
    """Find the second-highest win total, excluding the champion."""
    second_index = -1
    second_wins = -1
    for candidate_index in sorted(win_counts.keys()):
        is_champion = candidate_index == champion_index
        is_contender = is_champion is False
        if is_contender:
            candidate_wins = win_counts[candidate_index]
            stronger_found = candidate_wins > second_wins
            if stronger_found:
                second_index = candidate_index
                second_wins = candidate_wins
    runner_pair = (second_index, second_wins)
    return runner_pair


def select_champion_line():
    """Run the tournament tally and return the champion line and its record."""
    win_counts = tally_match_wins(TOURNAMENT_MATCHES)
    champion_pair = pick_highest_index(win_counts)
    champion_index = champion_pair[0]
    champion_wins = champion_pair[1]
    runner_pair = runner_up_index(win_counts, champion_index)
    runner_index = runner_pair[0]
    runner_wins = runner_pair[1]
    champion_line = champion_line_for_index(champion_index)
    selection_record = {
        "champion_index": champion_index,
        "champion_wins": champion_wins,
        "runner_up_index": runner_index,
        "runner_up_wins": runner_wins,
        "champion_line": champion_line,
    }
    return selection_record


def verify_expected_champion(selection_record):
    """Confirm the tally names the line the bracket was built around."""
    found_index = selection_record["champion_index"]
    matches_expected = found_index == EXPECTED_CHAMPION_INDEX
    return matches_expected


def prepare_output_directory(output_path):
    """Create the parent directory of the output file when it is missing."""
    parent_dir = os.path.dirname(output_path)
    dir_present = os.path.isdir(parent_dir)
    if dir_present:
        prepared_result = parent_dir
        return prepared_result
    os.makedirs(parent_dir, exist_ok=True)
    prepared_result = parent_dir
    return prepared_result


def encode_entry_text(text_line):
    """Encode a line as UTF-8 bytes, exactly as the gate reads them."""
    encoded_bytes = text_line.encode("utf-8")
    return encoded_bytes


def write_entry_file(output_path, text_line):
    """Write one line to the output path and return the bytes written."""
    prepared_dir = prepare_output_directory(output_path)
    encoded_bytes = encode_entry_text(text_line)
    written_count = 0
    try:
        handle = open(output_path, "wb")
        written_count = handle.write(encoded_bytes)
        handle.close()
    except OSError as write_error:
        error_message = "failed to write {}: {}".format(output_path, write_error)
        raise RuntimeError(error_message)
    write_record = {
        "directory": prepared_dir,
        "path": output_path,
        "bytes": written_count,
    }
    return write_record


def build_entry_text():
    """Select the champion, gate it, and return it ready to write."""
    selection_record = select_champion_line()
    expected_ok = verify_expected_champion(selection_record)
    if expected_ok is False:
        failure_message = "tournament tally named an unexpected champion"
        raise RuntimeError(failure_message)
    champion_line = selection_record["champion_line"]
    verdict_map = gate_check(champion_line)
    passes_gate = gate_passes(verdict_map)
    if passes_gate is False:
        gate_message = "champion line failed the gate: {}".format(verdict_map)
        raise RuntimeError(gate_message)
    built_record = {
        "line": champion_line,
        "chars": verdict_map["chars"],
        "selection": selection_record,
    }
    return built_record


def report_build(built_record, write_record):
    """Print a short human-readable summary of the run to stdout."""
    champion_line = built_record["line"]
    char_count = built_record["chars"]
    selection_record = built_record["selection"]
    champion_wins = selection_record["champion_wins"]
    runner_wins = selection_record["runner_up_wins"]
    output_path = write_record["path"]
    bytes_written = write_record["bytes"]
    summary_lines = [
        "champion: {}".format(champion_line),
        "characters: {}".format(char_count),
        "tournament: champion {} wins, runner-up {} wins".format(champion_wins, runner_wins),
        "wrote {} ({} bytes)".format(output_path, bytes_written),
    ]
    summary_text = "\n".join(summary_lines)
    print(summary_text)
    return summary_text


def main():
    """Entry point: build the line, write it, report the result."""
    built_record = build_entry_text()
    champion_line = built_record["line"]
    write_record = write_entry_file(OUTPUT_PATH, champion_line)
    report_build(built_record, write_record)
    exit_code = 0
    return exit_code


if __name__ == "__main__":
    main_status = main()
    sys.exit(main_status)

from tools.telegram import sanitize_message


def test_sanitize_message():
    # Test case 1: Unsupported div tag
    input_1 = "<div>Matches for Spanish Copa Del Rey are below:</div>"
    expected_1 = "Matches for Spanish Copa Del Rey are below:\n"
    assert sanitize_message(input_1) == expected_1, (
        f"Test 1 Failed: {sanitize_message(input_1)}"
    )

    # Test case 2: Unsupported ul and li tags
    input_2 = "<ul><li>Match 1</li><li>Match 2</li></ul>"
    # The sanitizer adds a newline after li, so we expect:
    # Match 1\nMatch 2\n
    # Note: ul is just unwrapped, li gets newline after insertion and then unwrapped.
    output_2 = sanitize_message(input_2)
    assert "Match 1" in output_2 and "Match 2" in output_2, f"Test 2 Failed: {output_2}"

    # Test case 3: Supported b tag
    input_3 = "<b>Bold Text</b>"
    expected_3 = "<b>Bold Text</b>"
    assert sanitize_message(input_3) == expected_3, (
        f"Test 3 Failed: {sanitize_message(input_3)}"
    )

    # Test case 4: Mixed content
    input_4 = "<div><b>Header</b></div><ul><li>Item 1</li></ul>"
    output_4 = sanitize_message(input_4)
    assert "<b>Header</b>" in output_4, f"Test 4 Failed: {output_4}"
    assert "Item 1" in output_4, f"Test 4 Failed: {output_4}"
    assert "<div>" not in output_4, f"Test 4 Failed: {output_4}"

    print("All tests passed!")


if __name__ == "__main__":
    test_sanitize_message()

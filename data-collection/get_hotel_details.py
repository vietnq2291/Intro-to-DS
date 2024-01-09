import argparse
import csv
import logging
import sys
import time
import traceback
from playwright.sync_api import sync_playwright, Page, expect

from hotel import Hotel
from hotel.writer.csv import HotelCsvWriter


def get_hotel_details(hotel_page: Page) -> Hotel:
    hotel_name = hotel_page.get_by_role("heading").first.inner_text()

    # About page
    hotel_page.locator("#details>span").first.click()
    # Sections in "About page"
    hotel_info_articles = hotel_page.locator("section")

    # About this hotel (usually the first article tag)
    about_panel = hotel_info_articles.filter(
        has=hotel_page.locator("h2.ZSxxwc:has-text('About this hotel')"),
        # has_text="About this hotel",
    ).first

    # Address & contact information
    address_contact_info = about_panel.locator(".U1L8Pd").nth(1)

    # First matching locator (nth=0): Address
    # Second one: Phone
    hotel_address = address_contact_info.locator(".GtAk2e").nth(0).inner_text()

    # amenities_panel = hotel_info_articles.filter(has_text="Amenities").nth(0)
    amenities_panel = hotel_info_articles.filter(
        has=hotel_page.locator("h2.ZSxxwc:has-text('Amenities')"),
        # has_text="About this hotel",
    ).first

    popular_amenities: list[str] = []
    try:
        popular_amenities_locator = amenities_panel.locator(".RhdAVb").nth(0)
        expect(popular_amenities_locator).to_be_visible(timeout=1000)
        popular_amenities_list = popular_amenities_locator.locator(".LtjZ2d")
        popular_amenities = [
            span.inner_text() for span in popular_amenities_list.all()
        ]
    except AssertionError as e:
        pass
    except TimeoutError as e:
        traceback.print_exc()

    # Photos page
    photo_count: int = 0
    try:
        hotel_page.locator("#photos>span").first.click()

        try:
            images_by_owner = hotel_page.get_by_label("By owner").nth(0)
            expect(images_by_owner).to_be_visible(timeout=2000)
            images_by_owner.click()
        except AssertionError as e:
            print("No photos from hotel's owner")
            pass
        else:
            photo_categories_locator = hotel_page.locator("h2.qUbkDc")
            expect(photo_categories_locator.nth(0)).to_be_in_viewport()
            hotel_page.keyboard.press("End", delay=200)

            # Each category has the following format: CATEGORY (number_of_photos)
            for heading in photo_categories_locator.all():
                category_with_count = heading.inner_text()
                open_pos = category_with_count.find("(")
                close_pos = category_with_count.find(")")
                category_photos_count_str = category_with_count[
                    open_pos + 1 : close_pos
                ]
                photo_count += int(
                    category_photos_count_str.replace(",", ""), base=10
                )
    except AssertionError | TimeoutError as e:
        traceback.print_exc()
        pass

    return Hotel(
        source="Google",
        name=hotel_name,
        address=hotel_address,
        images_count=photo_count,
        popular_amenities=popular_amenities,
    )


def main() -> None:
    arg_parser = argparse.ArgumentParser(
        description="Get hotel details from a list of URLs from Google Travel",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    arg_parser.add_argument(
        "input",
        type=str,
        help="Path to file containing hotel URLs",
    )
    arg_parser.add_argument(
        "--output",
        type=str,
        help="Path to output file",
        default=f"output/hotel-details-{int(time.time() * 1000)}.csv",
    )
    arg_parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Whether to run browser in headless mode",
    )
    args = arg_parser.parse_args()

    input_filename: str = args.input
    output_filename: str = args.output
    is_headless: bool = args.headless

    print(f"Running in headless mode: {is_headless}", file=sys.stderr)
    print(f"Reading from {input_filename}", file=sys.stderr)
    print(f"Writing to {output_filename}", file=sys.stderr)

    with (
        sync_playwright() as p,
        p.chromium.launch(headless=is_headless, timeout=5000) as browser,
        browser.new_context() as context,
        open(input_filename, "r", encoding="utf-8") as input_file,
        # open(
        #     output_filename,
        #     "w",
        #     newline="",
        #     encoding="utf-8",
        # ) as out_file,
        HotelCsvWriter(output_filename) as writer,
    ):
        hotel_page = context.new_page()

        # writer = csv.writer(out_file, quoting=csv.QUOTE_NONNUMERIC)
        # writer.writerow(
        #     [
        #         "name",
        #         "address",
        #         "images_count",
        #         "popular_amenities",
        #         "amenities",
        #         "source",
        #     ]
        # )

        for line_number, link in enumerate(input_file):
            hotel_page.goto(link)

            details = get_hotel_details(hotel_page)
            writer.append(details)
            # writer.writerow(
            #     [
            #         details.name,
            #         details.address,
            #         details.images_count,
            #         details.popular_amenities,
            #         "Google",
            #     ]
            # )


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd


seats = ['-'] * 100

VALID_SEATS = [
    11, 12, 13, 14, 15, 16, 17, 18,
    21, 22, 23, 24, 25, 26, 27, 28,
    31, 32, 33, 34, 35, 36, 37, 38,
    41, 42, 43, 44, 45, 46, 47, 48,
    51, 52, 53, 54, 55, 56, 57, 58,
]

def seat_available(seats_list, seat_number: int):
    if seat_number not in VALID_SEATS:
        return False, "Seat does not exist!"
    if seats_list[seat_number] != "-":
        return False, "Seat is already occupied!"
    return True, "Seat available"


def book_seat(seats_list, seat_number: int):
    ok, msg = seat_available(seats_list, seat_number)
    if not ok:
        return False, msg
    seats_list[seat_number] = "X"
    return True, "Seat selected successfully!"

# ----------Streamlit setup------------------

st.set_page_config(page_title="Seat Booking System", page_icon="🚌")

if "seats" not in st.session_state:
    st.session_state.seats = seats

if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "selected_seat" not in st.session_state:
    st.session_state.selected_seat = None

#---------- Seat grid--------- 

def render_seat_grid():
    seats_list = st.session_state.seats
    st.markdown("#### Coach – Seat Layout")

    st.markdown("🟩 = ____Available____; 🟥 = ___Booked___ ; 🟦 = ___Selected___", unsafe_allow_html=True,)

    for row in range(1, 9):
        c1, c2, c3, gap1, gap2, c4, c5 = st.columns([1, 1, 1, 0.3, 0.3, 1, 1])

        def draw_seat(col, col_number):
            if col_number is None:
                with col:
                    st.write(" ")
                return

            seat_num = col_number * 10 + row
            if seat_num not in VALID_SEATS:
                with col:
                    st.write(" ")
                return

            val = seats_list[seat_num]
            is_selected = (st.session_state.selected_seat == seat_num)

            if val == "-":
                emoji = "🟦" if is_selected else "🟩"
                disabled = False
            else:
                emoji = "🟥"
                disabled = True

            label = f"{emoji}\n{seat_num}"
            key = f"seat_{seat_num}"

            with col:
                clicked = st.button(label, key=key, disabled=disabled)
                if clicked and not disabled:
                    st.session_state.selected_seat = seat_num

        draw_seat(c1, 1)
        draw_seat(c2, 2)
        draw_seat(c3, 3)
        draw_seat(c4, 4)
        draw_seat(c5, 5)


#------- Main UI------------

st.title("🚌 Seat Booking System")

left_col, right_col = st.columns([1.2, 1])

# --- Left: seat grid ----------
with left_col:
    st.subheader("Choose Seat")

    render_seat_grid()

    if st.session_state.selected_seat is not None:
        seat = st.session_state.selected_seat
        row = seat % 10
        col_n = seat // 10
        st.info(f"Selected Seat: *{seat}* (Column {col_n}, Row {row})")

# --- Right: passenger form ---
with right_col:
    st.subheader("Passenger Details")

    with st.form("booking_form"):
        name = st.text_input("Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        location = st.text_input("Location (From)")
        destination = st.text_input("Destination (To)")

        current_seat = st.session_state.selected_seat
        st.text(f"Selected Seat: {current_seat if current_seat else 'None'}")

        submit = st.form_submit_button("Confirm Booking ✅")

    if submit:
        seats_list = st.session_state.seats
        seat_number = st.session_state.selected_seat

        if not all([name, phone, email, location, destination]):
            st.error("Please fill in all passenger details.")
        elif seat_number is None:
            st.error("Please select a seat from the left pane.")
        else:
            ok, msg = book_seat(seats_list, int(seat_number))
            if not ok:
                st.error(msg)
            else:
                row = seat_number % 10
                col_n = seat_number // 10

                booking_record = {
                    "Name": name,
                    "phone_number": phone,
                    "email_id": email,
                    "location": location,
                    "destination": destination,
                    "seat_number": int(seat_number),
                    "Column": col_n,
                    "Row": row,
                }
                st.session_state.bookings.append(booking_record)

                st.success("🎉 Booking Confirmed!")
                st.write(f"*Name:* {name}")
                st.write(f"*Email:* {email}")
                st.write(f"*Phone:* {phone}")
                st.write(f"*From:* {location}")
                st.write(f"*To:* {destination}")
                st.write(f"*Seat Booked:*  (Seat {seat_number})")
                st.write("Thank you for booking with us!")

                st.session_state.selected_seat = None

if st.session_state.bookings:
    st.markdown("---")
    st.subheader("All Bookings (this session)")

    # ----Converting to Table(DataFrame)----
    df = pd.DataFrame(st.session_state.bookings)
    st.table(df)

    # ----Create CSV and add download button---- 
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download bookings as CSV",
        data=csv,
        file_name="bookings.csv",
        mime="text/csv",
    )
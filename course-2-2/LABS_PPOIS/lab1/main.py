from cli import HotelCLI

if __name__ == "__main__":
    try:
        HotelCLI().cmdloop()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
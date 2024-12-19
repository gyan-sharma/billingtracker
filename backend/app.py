import pandas as pd
import os
import calendar
import re

# Configuration Switch
ROUND_TO_INTEGER = True  # Set to False to keep decimals for TOTAL PRICE

def clean_column(value):
    """Clean column values: strip spaces, uppercase, remove invisible characters."""
    return str(value).strip().upper().replace('\u200b', '').replace('\ufeff', '')

def month_number_to_name(month):
    """Convert month number to month name."""
    try:
        month_num = int(month)
        return calendar.month_name[month_num] if 1 <= month_num <= 12 else "Invalid Month"
    except:
        return "Invalid Month"

def generate_unique_id(row):
    """Generate a UNIQUE_ID by combining SERVICE NAME, TYPE, and SIZE."""
    return f"{row['SERVICE NAME']}_{row['TYPE']}_{row['SIZE']}"

def auto_adjust_column_widths(writer, df, sheet_name):
    """Auto-fit column widths to match the content."""
    worksheet = writer.sheets[sheet_name]
    for i, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
        worksheet.set_column(i, i, max_len)

def create_dashboard(writer, consolidated_df, organization_summary_df, application_summary_df, component_usage_df):
    """Generate a text-based dashboard with useful summary tables."""
    workbook = writer.book
    worksheet = workbook.add_worksheet("Dashboard")
    writer.sheets["Dashboard"] = worksheet

    # Formatting
    bold_format = workbook.add_format({'bold': True, 'font_size': 12})
    header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#DCE6F1'})
    number_format = workbook.add_format({'num_format': '#,##0', 'align': 'center'})
    text_format_left = workbook.add_format({'align': 'left'})

    row = 2  # Starting row

    # --- Table 1: Top 15 Organizations by Total Price ---
    worksheet.write(row, 1, 'Top 15 Organizations by Total Price', bold_format)
    row += 1
    top_organizations = (
        organization_summary_df
        .groupby("ORGANIZATION NAME", as_index=False)['TOTAL PRICE']
        .sum()
        .sort_values(by='TOTAL PRICE', ascending=False)
        .head(15)
    )
    worksheet.write_row(row, 1, ['Organization Name', 'Total Price'], header_format)
    row += 1
    for org in top_organizations.itertuples():
        worksheet.write_row(row, 1, [org[1], org[2]], text_format_left)
        row += 1
    row += 2  # Empty space after table

    # --- Table 2: Top 15 Applications by Total Price ---
    worksheet.write(row, 1, 'Top 15 Applications by Total Price', bold_format)
    row += 1
    top_applications = application_summary_df.nlargest(15, 'TOTAL PRICE')
    worksheet.write_row(row, 1, ['Organization Name', 'Workspace Group', 'Application Name', 'Total Price'], header_format)
    row += 1
    for app in top_applications.itertuples():
        worksheet.write_row(row, 1, [app[1], app[2], app[3], app[6]], text_format_left)
        row += 1
    row += 2  # Empty space after table

    # --- Table 3: Top 15 Components by Hours Used ---
    worksheet.write(row, 1, 'Top 15 Components by Hours Used', bold_format)
    row += 1
    top_components = (
        consolidated_df
        .groupby(['SERVICE NAME', 'WORKSPACE GROUP'])['HOURS USED']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .head(15)
    )
    worksheet.write_row(row, 1, ['Service Name', 'Workspace Group', 'Hours Used'], header_format)
    row += 1
    for comp in top_components.itertuples():
        worksheet.write_row(row, 1, [comp[1], comp[2], comp[3]], text_format_left)
        row += 1
    row += 2  # Empty space after table

    # --- Table 4: Count of Components with Hours > 0 ---
    worksheet.write(row, 1, 'Count of Components with Hours > 0', bold_format)
    row += 1
    component_usage_summary = (
        component_usage_df.groupby('SERVICE NAME')['COUNT']
        .sum()
        .reset_index()
        .sort_values(by='COUNT', ascending=False)
    )
    worksheet.write_row(row, 1, ['Service Name', 'Count'], header_format)
    row += 1
    for comp in component_usage_summary.itertuples():
        worksheet.write_row(row, 1, [comp[1], comp[2]], text_format_left)
        row += 1

    # Adjust column widths for dashboard
    for col in range(6):
        worksheet.set_column(col, col, 20)

def process_usage_and_price(uploads_folder, price_file, summary_output_file, detailed_output_file):
    print("Starting the script...")

    # Step 1: Read and clean pricing data
    pricing_df = pd.read_excel(price_file)
    pricing_df.columns = pricing_df.columns.str.strip().str.upper()
    for col in ['PRETTY_NAME', 'TYPE', 'SIZE']:
        pricing_df[col] = pricing_df[col].apply(clean_column)

    pricing_df['UNIQUE_ID'] = pricing_df.apply(lambda row: f"{row['PRETTY_NAME']}_{row['TYPE']}_{row['SIZE']}", axis=1)
    pricing_dict = dict(zip(pricing_df['UNIQUE_ID'], pricing_df['PRICE']))

    master_list = []
    missing_ids_list = []
    detailed_sheets = {}

    # Step 2: Process usage files
    for file in os.listdir(uploads_folder):
        if file.endswith(".xlsx") and file != 'Price.xlsx':  # Skip Price.xlsx file
            match = re.match(r"(.*?)_\d{2}_(\d{4})_Usage\.xlsx", file)
            if match:
                organization_name = match.group(1)
                year = match.group(2)
                file_path = os.path.join(uploads_folder, file)

                for sheet in pd.ExcelFile(file_path).sheet_names:
                    if re.match(r"^TOTAL .* \d{4}$", sheet.upper()):
                        continue

                    usage_df = pd.read_excel(file_path, sheet_name=sheet)
                    usage_df.columns = usage_df.columns.str.strip().str.upper()

                    for col in ['SERVICE NAME', 'TYPE', 'SIZE', 'APPLICATION NAME', 'MONTH']:
                        if col in usage_df.columns:
                            usage_df[col] = usage_df[col].apply(clean_column)

                    usage_df['TYPE'] = usage_df['TYPE'].str.upper()
                    usage_df['SIZE'] = usage_df['SIZE'].str.upper()
                    usage_df['ORGANIZATION NAME'] = organization_name
                    usage_df['YEAR'] = int(year)
                    usage_df['MONTH'] = usage_df['MONTH'].apply(month_number_to_name)
                    usage_df['WORKSPACE GROUP'] = sheet
                    usage_df['UNIQUE_ID'] = usage_df.apply(generate_unique_id, axis=1)
                    usage_df['PRICE'] = usage_df['UNIQUE_ID'].map(pricing_dict).fillna(0)
                    usage_df['HOURS USED'] = pd.to_numeric(usage_df['HOURS USED'], errors='coerce').fillna(0)
                    usage_df['TOTAL PRICE'] = (usage_df['PRICE'] * usage_df['HOURS USED']).round(0) if ROUND_TO_INTEGER else usage_df['PRICE'] * usage_df['HOURS USED']

                    usage_df = usage_df.sort_values(by='TOTAL PRICE', ascending=False)
                    master_list.append(usage_df)
                    detailed_sheets[f"{organization_name}_{sheet}"] = usage_df

    # Step 3: Generate consolidated and summary data
    consolidated_df = pd.concat(master_list, ignore_index=True).sort_values(by='TOTAL PRICE', ascending=False)
    organization_summary_df = consolidated_df.groupby(['ORGANIZATION NAME', 'WORKSPACE GROUP', 'MONTH', 'YEAR'], as_index=False)[['HOURS USED', 'TOTAL PRICE']].sum().sort_values(by='TOTAL PRICE', ascending=False)
    application_summary_df = consolidated_df.groupby(['ORGANIZATION NAME', 'WORKSPACE GROUP', 'APPLICATION NAME', 'MONTH', 'YEAR'], as_index=False)['TOTAL PRICE'].sum().sort_values(by='TOTAL PRICE', ascending=False)
    component_usage_df = (
        consolidated_df[consolidated_df['HOURS USED'] > 0]
        .groupby(['SERVICE NAME'])
        .size()
        .reset_index(name='COUNT')
    )

    # Create necessary folders if they don't exist
    os.makedirs(uploads_folder, exist_ok=True)
    os.makedirs(os.path.dirname(summary_output_file), exist_ok=True)
    os.makedirs(os.path.dirname(detailed_output_file), exist_ok=True)

    # Step 4: Save summary file
    with pd.ExcelWriter(summary_output_file, engine='xlsxwriter') as writer:
        consolidated_df.to_excel(writer, sheet_name="Consolidated Data", index=False)
        organization_summary_df.to_excel(writer, sheet_name="Organization Summary", index=False)
        application_summary_df.to_excel(writer, sheet_name="Application Summary", index=False)
        create_dashboard(writer, consolidated_df, organization_summary_df, application_summary_df, component_usage_df)
        auto_adjust_column_widths(writer, consolidated_df, "Consolidated Data")
        auto_adjust_column_widths(writer, organization_summary_df, "Organization Summary")
        auto_adjust_column_widths(writer, application_summary_df, "Application Summary")

    # Step 5: Save detailed output file
    with pd.ExcelWriter(detailed_output_file, engine='xlsxwriter') as writer:
        for sheet_name, df in detailed_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            auto_adjust_column_widths(writer, df, sheet_name[:31])

if __name__ == "__main__":
    folder_path = os.getcwd()
    uploads_folder = os.path.join(folder_path, 'uploads')
    price_file = os.path.join(uploads_folder, 'Price.xlsx')  # Updated path to uploads folder
    summary_output_file = os.path.join(folder_path, 'outputs', 'Summary_Output.xlsx')
    detailed_output_file = os.path.join(folder_path, 'outputs', 'Detailed_Output.xlsx')

    process_usage_and_price(uploads_folder, price_file, summary_output_file, detailed_output_file)
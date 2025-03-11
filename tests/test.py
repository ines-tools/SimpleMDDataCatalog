from SimpleMDDataCatalog.spreadsheet_to_ld import spreadsheet_to_ld_catalog


spreadsheet_to_ld_catalog(uri="https://www.test.com#", output_graph='tests/test_AI.ttl', input_sheet='tests/catalog_ai.xlsx')
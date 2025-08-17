DEATH_CERTIFICATE = """
STATE OF NEW YORK DEPARTMENT OF HEALTH

CERTIFICATE OF DEATH

Certificate Number: 2023-NY-00012345

1. Full Name of Deceased: Johnathan Edward Doe
2. Date of Death: January 1, 2023
3. Place of Death: New York-Presbyterian Hospital, New York, NY
4. Sex: Male
5. Age at Death: 76 years
6. Date of Birth: March 5, 1946
7. Social Security Number: 123-45-6789
8. Usual Residence: 789 Elm Street, Albany, NY 12207
9. Marital Status: Married
10. Name of Spouse: Margaret Anne Doe
11. Occupation: Retired Attorney
12. Informant Name: Michael Doe
13. Relationship to Deceased: Son
14. Cause of Death: Acute Myocardial Infarction
15. Certifying Physician: Dr. Linda Park, M.D.
16. Date Signed: January 2, 2023

Filed with the New York Department of Health
Date Received: January 3, 2023
Registrar: Helen T. Vaughn
"""

WILL_DOCUMENT = """
LAST WILL AND TESTAMENT

I, Robert James Smith, residing at 456 Oak Avenue, Boston, MA 02101, being of sound mind and memory, do hereby declare this to be my Last Will and Testament, revoking all previous wills and codicils.

ARTICLE I - EXECUTOR
I appoint my daughter, Sarah Smith Johnson, as Executor of this Will. If she is unable or unwilling to serve, I appoint my son, David Michael Smith, as alternate Executor.

ARTICLE II - BENEFICIARIES
I give, devise, and bequeath my estate as follows:

1. To my beloved wife, Mary Elizabeth Smith, I leave our primary residence and all personal property therein.
2. To my daughter, Sarah Smith Johnson, I leave 40% of my remaining assets.
3. To my son, David Michael Smith, I leave 40% of my remaining assets.
4. To my grandson, Timothy Johnson, I leave 20% of my remaining assets for his education.

ARTICLE III - DEBTS AND TAXES
I direct my Executor to pay all my just debts, funeral expenses, and estate taxes from my estate.

IN WITNESS WHEREOF, I have hereunto set my hand and seal this 15th day of June, 2022.

___________________________
Robert James Smith, Testator

Witnessed by:
___________________________
John D. Anderson
___________________________
Patricia L. Williams
"""

PROPERTY_DEED = """
WARRANTY DEED

THIS DEED, made this 10th day of September, 2023, between John Michael Thompson and Jane Marie Thompson, husband and wife (hereinafter "Grantor"), and Estate of Richard Thompson (hereinafter "Grantee").

WITNESSETH, that the Grantor, for and in consideration of Ten Dollars ($10.00) and other good and valuable consideration, the receipt of which is hereby acknowledged, does hereby grant, bargain, sell and convey unto the Grantee, the following described real property:

PROPERTY DESCRIPTION:
Lot 15, Block 7, Riverside Estates Subdivision, as recorded in Plat Book 23, Page 45, in the Office of the County Recorder, Jefferson County, State of Colorado.

PARCEL NUMBER: 123-456-789-000

PROPERTY ADDRESS: 123 River Road, Denver, CO 80201

Together with all improvements, fixtures, and appurtenances thereto belonging.

TO HAVE AND TO HOLD the same unto the Grantee, its heirs and assigns forever.

The Grantor covenants that they are lawfully seized of said premises in fee simple and have good right to convey the same.

IN WITNESS WHEREOF, the Grantor has executed this deed on the date first above written.

___________________________
John Michael Thompson

___________________________
Jane Marie Thompson

State of Colorado
County of Jefferson

Acknowledged before me this 10th day of September, 2023
___________________________
Notary Public
"""

FINANCIAL_STATEMENT = """
BANK OF AMERICA
ESTATE ACCOUNT STATEMENT

Account Name: Estate of Margaret Wilson
Account Number: ****4567
Statement Period: January 1, 2023 - January 31, 2023

ACCOUNT SUMMARY
Beginning Balance (01/01/2023): $125,750.00
Total Deposits: $45,000.00
Total Withdrawals: $12,500.00
Ending Balance (01/31/2023): $158,250.00

TRANSACTION DETAILS
Date        Description                          Debit       Credit      Balance
01/05/2023  Life Insurance Proceeds                          $45,000.00  $170,750.00
01/10/2023  Funeral Expenses                    $8,500.00               $162,250.00
01/15/2023  Legal Fees - Estate Administration  $2,000.00               $160,250.00
01/25/2023  Utility Payments                    $2,000.00               $158,250.00

ACCOUNT HOLDINGS
Checking Account: $58,250.00
Savings Account: $100,000.00
Total Assets: $158,250.00

This statement is provided for the estate administration purposes.
For questions, contact Estate Services at 1-800-123-4567.
"""

TAX_DOCUMENT = """
Form 1041 - U.S. Income Tax Return for Estates and Trusts
Tax Year 2022

Estate Information:
Name of Estate: Estate of William Charles Brown
EIN: 12-3456789
Date of Death: November 15, 2022

Income:
1. Interest Income: $5,234.00
2. Dividend Income: $12,456.00
3. Capital Gains: $25,000.00
4. Rental Income: $18,000.00
Total Income: $60,690.00

Deductions:
1. Attorney Fees: $5,000.00
2. Accounting Fees: $2,500.00
3. Executor Fees: $3,000.00
4. Other Deductions: $1,500.00
Total Deductions: $12,000.00

Taxable Income: $48,690.00
Tax Liability: $11,685.60

Prepared by: Johnson & Associates CPAs
Date: March 15, 2023
Preparer PTIN: P12345678
"""

INVALID_DEATH_CERTIFICATE = """
DEATH RECORD

Name: Jane Doe
Died: Sometime in 2023
Location: Hospital

This is a death record but missing required fields.
"""

INVALID_WILL = """
DOCUMENT OF INHERITANCE

I leave everything to my children.

Signed,
John Smith
"""

MISCELLANEOUS_DOCUMENT = """
CORRESPONDENCE

Dear Estate Administrator,

We are writing to confirm receipt of the documents submitted for the estate of Mr. Johnson.
Please note that additional documentation may be required to complete the processing.

We will review the submitted materials and contact you within 10 business days.

Thank you for your patience.

Sincerely,
Estate Services Department
ABC Insurance Company
"""

MOCK_DOCUMENTS = {
    "death_certificate_valid": {
        "document_id": "DOC-001",
        "content": DEATH_CERTIFICATE,
        "metadata": {"source": "NY Department of Health", "expected_category": "Death Certificate"}
    },
    "will_valid": {
        "document_id": "DOC-002",
        "content": WILL_DOCUMENT,
        "metadata": {"source": "Legal Office", "expected_category": "Will or Trust"}
    },
    "property_deed": {
        "document_id": "DOC-003",
        "content": PROPERTY_DEED,
        "metadata": {"source": "County Recorder", "expected_category": "Property Deed"}
    },
    "financial_statement": {
        "document_id": "DOC-004",
        "content": FINANCIAL_STATEMENT,
        "metadata": {"source": "Bank of America", "expected_category": "Financial Statement"}
    },
    "tax_document": {
        "document_id": "DOC-005",
        "content": TAX_DOCUMENT,
        "metadata": {"source": "IRS", "expected_category": "Tax Document"}
    },
    "invalid_death_certificate": {
        "document_id": "DOC-006",
        "content": INVALID_DEATH_CERTIFICATE,
        "metadata": {"source": "Unknown", "expected_category": "Death Certificate", "should_fail_compliance": True}
    },
    "invalid_will": {
        "document_id": "DOC-007",
        "content": INVALID_WILL,
        "metadata": {"source": "Unknown", "expected_category": "Will or Trust", "should_fail_compliance": True}
    },
    "miscellaneous": {
        "document_id": "DOC-008",
        "content": MISCELLANEOUS_DOCUMENT,
        "metadata": {"source": "Insurance Company", "expected_category": "Miscellaneous"}
    }
}
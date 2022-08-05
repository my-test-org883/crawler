p4_client = [
    {
        "Client": "TEMPLATE_D4_A50-LTN-OPEN_QQREL",
        "View": [
            //",
            (
                ///"
                "bootloader/images/..."
            ),
            //",
            (
                ///"
                "device/a50_common/..."
            ),
            //",
            (
                ///"
                "vendor/a50_common/..."
            ),
            //",
            (
                ///"
                "a50_ltn_open/... TEMPLATE_PEjndwobdoquhdqo"
            ),
            "//QUEEN_CSC/Strawberry/EXYNOS5/a50/...",
            //",
            //",
            "//",
        ],
    }
]

p4_client_side_effect = [p4_client for _ in range(10)]

p4_changes_side_effect = [
    [
        {"change": "19111111"},
        {"change": "19222222"},
        {"change": "12131415"},
        {"change": "12131214"},
        {"change": "12131215"},
        {"change": "12131212"},
        {"change": "12131213"},
        {"change": "12131217"},
        {"change": "12345678"},
    ],
    [{"change": "1766666"}, {"change": "1788888"}, {"change": "19734567"}],
    [{"change": "19333333"}, {"change": "19444444"}],
]

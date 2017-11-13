//todo: future implementations should use this when doing simple operations on huge data sets

#define GET_UINT_BIT_EXPANDED( input_array, pos )\
    input_array[pos/32] & 1<<pos%32 != 0

#define SET_UINT_BIT_EXPANDED( input_array, pos )\
    input_array[pos/32] |=  1<<pos%32
# from iqoptionapi.stable_api import IQ_Option
# from flask import Flask, request, jsonify
# import requests
# from langchain_google_genai import ChatGoogleGenerativeAI

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash-thinking-exp-01-21",
#     temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
#     google_api_key='AIzaSyCH0lltb7Gs31c0zoLlljI4UIeDo2mb1cc'
#     # other params...
# )

# def signal(pair, ofset):

#     headers = {
#     'Authorization': 'Bearer 8874b89990ef31aa9fd85b4e3765f222-b4f234623b1f9f383de395ea4910ff6a'
# }

#     url_hist1 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M1&count={ofset}'
#     url_hist2 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M2&count={ofset}'
#     url_hist5 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M5&count={ofset}'

#     response1 = requests.get(url_hist1, headers=headers)
#     response2 = requests.get(url_hist2, headers=headers)
#     response5 = requests.get(url_hist5, headers=headers)
#     f1 = response1.json()
#     f2 = response2.json()
#     f5 = response5.json()
    
#     data1=[]
#     data2=[]
#     data5=[]
#     for m in f1['candles']:

#       if (m['complete']) :

#         f = {
#              'time': m['time'],
#              'volume': m['volume'],
#              'open': m['mid']['o'],
#              'close': m['mid']['c'],
#              'max': m['mid']['h'],
#              'min': m['mid']['l']
#            };
#         data1.append(f);

#     for m in f2['candles']:

#       if (m['complete']) :

#         f = {
#              'time': m['time'],
#              'volume': m['volume'],
#              'open': m['mid']['o'],
#              'close': m['mid']['c'],
#              'max': m['mid']['h'],
#              'min': m['mid']['l']
#            };
#         data2.append(f);

#     for m in f5['candles']:

#       if (m['complete']) :

#         f = {
#              'time': m['time'],
#              'volume': m['volume'],
#              'open': m['mid']['o'],
#              'close': m['mid']['c'],
#              'max': m['mid']['h'],
#              'min': m['mid']['l']
#            };
#         data5.append(f);   
    
#     # data1=[
#     #     {key: d[key] for key in [ 'time', 'o', 'c', 'h', 'l', 'volume']}
#     #     for d in f1['candles']
#     # ]
    
    
#     # data2=[
#     #     {key: d[key] for key in [ 'time', 'o', 'c', 'h', 'l', 'volume']}
#     #     for d in f2['candles']
#     # ]
#     # data5=[
#     #     {key: d[key] for key in [ 'time', 'o', 'c', 'h', 'l', 'volume']}
#     #     for d in f5['candles']
#     # ]
#     # data1.pop()
#     # data2.pop()
#     # data5.pop()
#     # print(data1)





#     # API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
#     # API.connect()
#     # a=API.get_server_timestamp()


#     # velas1 = API.get_candles(pair, 60, ofset, a)
#     # data1 = [
#     #     {key: d[key] for key in ['from', 'to', 'open', 'close', 'min', 'max', 'volume']}
#     #     for d in velas1
#     # ]
#     # data1.pop()


#     # velas2 = API.get_candles(pair, 120, ofset, a)
#     # data2 = [
#     #     {key: d[key] for key in ['from', 'to', 'open', 'close', 'min', 'max', 'volume']}
#     #     for d in velas2
#     # ]
#     # data2.pop()


#     # velas5 = API.get_candles(pair, 300, ofset, a)
#     # data5 = [
#     #     {key: d[key] for key in ['from', 'to', 'open', 'close', 'min', 'max', 'volume']}
#     #     for d in velas5
#     # ]
#     # data5.pop()


#     PROMPT=F"""Analyze the provided candlestick data for the 1-minute, 2-minute, and 5-minute timeframes using CWRV and price action combined Strategy and predict the direction of the next candle using CWRV and price action combined Strategy  for each timeframe. Based on your analysis, respond with CALL if you predict an upward movement across all three timeframes, PUT if you predict a downward movement across all three timeframes, or NEUTRAL if there is no clear direction or if the timeframes do not align. Only provide a signal (CALL or PUT) if all three timeframes show the same direction and you are 100% confident in your prediction. If there is any uncertainty or inconsistency between the timeframes, respond with NEUTRAL. Your response must be strictly in one word: CALL, PUT, or NEUTRAL.

#     Data:
#     1-Minute:{data1}

#     2-Minute: {data2}

#     5-Minute: {data5}

#     """

#     return PROMPT

# messages = [
#     (
#         "system",
#         "Analyze the provided candlestick data for the 1-minute, 2-minute, and 5-minute timeframes using CWRV and price action combined Strategy and predict the direction of the next candle using CWRV and price action combined Strategy  for each timeframe. Based on your analysis, respond with CALL if you predict an upward movement across all three timeframes, PUT if you predict a downward movement across all three timeframes, or NEUTRAL if there is no clear direction or if the timeframes do not align. Only provide a signal (CALL or PUT) if all three timeframes show the same direction and you are 100% confident in your prediction. If there is any uncertainty or inconsistency between the timeframes, respond with NEUTRAL. Your response must be strictly in one word: CALL, PUT, or NEUTRAL.",
#     ),
#     ("human", "Analyze the provided candlestick data for the 1-minute, 2-minute, and 5-minute timeframes using CWRV and price action combined Strategy and predict the direction of the next candle using CWRV and price action combined Strategy  for each timeframe. Based on your analysis, respond with CALL if you predict an upward movement across all three timeframes, PUT if you predict a downward movement across all three timeframes, or NEUTRAL if there is no clear direction or if the timeframes do not align. Only provide a signal (CALL or PUT) if all three timeframes show the same direction and you are 100% confident in your prediction. If there is any uncertainty or inconsistency between the timeframes, respond with NEUTRAL. Your response must be strictly in one word: CALL, PUT, or NEUTRAL.\n    Data:\n    1-Minute:[{'time': '2024-12-23T03:59:00.000000000Z', 'volume': 39, 'open': '1.04389', 'close': '1.04395', 'max': '1.04395', 'min': '1.04384'}, {'time': '2024-12-23T04:00:00.000000000Z', 'volume': 31, 'open': '1.04394', 'close': '1.04400', 'max': '1.04400', 'min': '1.04390'}, {'time': '2024-12-23T04:01:00.000000000Z', 'volume': 51, 'open': '1.04400', 'close': '1.04396', 'max': '1.04400', 'min': '1.04396'}, {'time': '2024-12-23T04:02:00.000000000Z', 'volume': 26, 'open': '1.04397', 'close': '1.04396', 'max': '1.04398', 'min': '1.04394'}, {'time': '2024-12-23T04:03:00.000000000Z', 'volume': 22, 'open': '1.04396', 'close': '1.04396', 'max': '1.04401', 'min': '1.04396'}, {'time': '2024-12-23T04:04:00.000000000Z', 'volume': 27, 'open': '1.04396', 'close': '1.04396', 'max': '1.04396', 'min': '1.04391'}, {'time': '2024-12-23T04:05:00.000000000Z', 'volume': 8, 'open': '1.04396', 'close': '1.04396', 'max': '1.04396', 'min': '1.04396'}, {'time': '2024-12-23T04:06:00.000000000Z', 'volume': 24, 'open': '1.04396', 'close': '1.04398', 'max': '1.04398', 'min': '1.04390'}, {'time': '2024-12-23T04:07:00.000000000Z', 'volume': 19, 'open': '1.04398', 'close': '1.04397', 'max': '1.04400', 'min': '1.04396'}, {'time': '2024-12-23T04:08:00.000000000Z', 'volume': 14, 'open': '1.04398', 'close': '1.04397', 'max': '1.04398', 'min': '1.04397'}, {'time': '2024-12-23T04:09:00.000000000Z', 'volume': 14, 'open': '1.04398', 'close': '1.04394', 'max': '1.04398', 'min': '1.04392'}, {'time': '2024-12-23T04:10:00.000000000Z', 'volume': 25, 'open': '1.04395', 'close': '1.04404', 'max': '1.04404', 'min': '1.04395'}, {'time': '2024-12-23T04:11:00.000000000Z', 'volume': 52, 'open': '1.04404', 'close': '1.04412', 'max': '1.04412', 'min': '1.04398'}, {'time': '2024-12-23T04:12:00.000000000Z', 'volume': 10, 'open': '1.04412', 'close': '1.04412', 'max': '1.04414', 'min': '1.04412'}]\n\n    2-Minute: [{'time': '2024-12-23T03:44:00.000000000Z', 'volume': 42, 'open': '1.04402', 'close': '1.04410', 'max': '1.04412', 'min': '1.04402'}, {'time': '2024-12-23T03:46:00.000000000Z', 'volume': 62, 'open': '1.04409', 'close': '1.04400', 'max': '1.04410', 'min': '1.04398'}, {'time': '2024-12-23T03:48:00.000000000Z', 'volume': 82, 'open': '1.04400', 'close': '1.04410', 'max': '1.04410', 'min': '1.04400'}, {'time': '2024-12-23T03:50:00.000000000Z', 'volume': 93, 'open': '1.04410', 'close': '1.04405', 'max': '1.04426', 'min': '1.04404'}, {'time': '2024-12-23T03:52:00.000000000Z', 'volume': 74, 'open': '1.04404', 'close': '1.04401', 'max': '1.04404', 'min': '1.04391'}, {'time': '2024-12-23T03:54:00.000000000Z', 'volume': 40, 'open': '1.04402', 'close': '1.04406', 'max': '1.04410', 'min': '1.04401'}, {'time': '2024-12-23T03:56:00.000000000Z', 'volume': 67, 'open': '1.04404', 'close': '1.04394', 'max': '1.04405', 'min': '1.04393'}, {'time': '2024-12-23T03:58:00.000000000Z', 'volume': 66, 'open': '1.04395', 'close': '1.04395', 'max': '1.04395', 'min': '1.04384'}, {'time': '2024-12-23T04:00:00.000000000Z', 'volume': 82, 'open': '1.04394', 'close': '1.04396', 'max': '1.04400', 'min': '1.04390'}, {'time': '2024-12-23T04:02:00.000000000Z', 'volume': 48, 'open': '1.04397', 'close': '1.04396', 'max': '1.04401', 'min': '1.04394'}, {'time': '2024-12-23T04:04:00.000000000Z', 'volume': 35, 'open': '1.04396', 'close': '1.04396', 'max': '1.04396', 'min': '1.04391'}, {'time': '2024-12-23T04:06:00.000000000Z', 'volume': 43, 'open': '1.04396', 'close': '1.04397', 'max': '1.04400', 'min': '1.04390'}, {'time': '2024-12-23T04:08:00.000000000Z', 'volume': 28, 'open': '1.04398', 'close': '1.04394', 'max': '1.04398', 'min': '1.04392'}, {'time': '2024-12-23T04:10:00.000000000Z', 'volume': 77, 'open': '1.04395', 'close': '1.04412', 'max': '1.04412', 'min': '1.04395'}]\n\n    5-Minute: [{'time': '2024-12-23T03:00:00.000000000Z', 'volume': 234, 'open': '1.04406', 'close': '1.04402', 'max': '1.04412', 'min': '1.04386'}, {'time': '2024-12-23T03:05:00.000000000Z', 'volume': 146, 'open': '1.04402', 'close': '1.04400', 'max': '1.04412', 'min': '1.04392'}, {'time': '2024-12-23T03:10:00.000000000Z', 'volume': 156, 'open': '1.04399', 'close': '1.04407', 'max': '1.04412', 'min': '1.04396'}, {'time': '2024-12-23T03:15:00.000000000Z', 'volume': 138, 'open': '1.04408', 'close': '1.04390', 'max': '1.04408', 'min': '1.04387'}, {'time': '2024-12-23T03:20:00.000000000Z', 'volume': 140, 'open': '1.04392', 'close': '1.04408', 'max': '1.04408', 'min': '1.04392'}, {'time': '2024-12-23T03:25:00.000000000Z', 'volume': 102, 'open': '1.04408', 'close': '1.04402', 'max': '1.04411', 'min': '1.04400'}, {'time': '2024-12-23T03:30:00.000000000Z', 'volume': 117, 'open': '1.04403', 'close': '1.04412', 'max': '1.04412', 'min': '1.04395'}, {'time': '2024-12-23T03:35:00.000000000Z', 'volume': 100, 'open': '1.04412', 'close': '1.04418', 'max': '1.04421', 'min': '1.04410'}, {'time': '2024-12-23T03:40:00.000000000Z', 'volume': 121, 'open': '1.04418', 'close': '1.04406', 'max': '1.04422', 'min': '1.04400'}, {'time': '2024-12-23T03:45:00.000000000Z', 'volume': 162, 'open': '1.04405', 'close': '1.04410', 'max': '1.04412', 'min': '1.04398'}, {'time': '2024-12-23T03:50:00.000000000Z', 'volume': 199, 'open': '1.04410', 'close': '1.04407', 'max': '1.04426', 'min': '1.04391'}, {'time': '2024-12-23T03:55:00.000000000Z', 'volume': 141, 'open': '1.04406', 'close': '1.04395', 'max': '1.04407', 'min': '1.04384'}, {'time': '2024-12-23T04:00:00.000000000Z', 'volume': 157, 'open': '1.04394', 'close': '1.04396', 'max': '1.04401', 'min': '1.04390'}, {'time': '2024-12-23T04:05:00.000000000Z', 'volume': 79, 'open': '1.04396', 'close': '1.04394', 'max': '1.04400', 'min': '1.04390'}]"),
#      ("ai", "CALL"),
#      ("human","Analyze the provided candlestick data for the 1-minute, 2-minute, and 5-minute timeframes using CWRV and price action combined Strategy and predict the direction of the next candle using CWRV and price action combined Strategy  for each timeframe. Based on your analysis, respond with CALL if you predict an upward movement across all three timeframes, PUT if you predict a downward movement across all three timeframes, or NEUTRAL if there is no clear direction or if the timeframes do not align. Only provide a signal (CALL or PUT) if all three timeframes show the same direction and you are 100% confident in your prediction. If there is any uncertainty or inconsistency between the timeframes, respond with NEUTRAL. Your response must be strictly in one word: CALL, PUT, or NEUTRAL.\n    Data:\n    1-Minute:[{'time': '2024-12-23T04:01:00.000000000Z', 'volume': 51, 'open': '1.04400', 'close': '1.04396', 'max': '1.04400', 'min': '1.04396'}, {'time': '2024-12-23T04:02:00.000000000Z', 'volume': 26, 'open': '1.04397', 'close': '1.04396', 'max': '1.04398', 'min': '1.04394'}, {'time': '2024-12-23T04:03:00.000000000Z', 'volume': 22, 'open': '1.04396', 'close': '1.04396', 'max': '1.04401', 'min': '1.04396'}, {'time': '2024-12-23T04:04:00.000000000Z', 'volume': 27, 'open': '1.04396', 'close': '1.04396', 'max': '1.04396', 'min': '1.04391'}, {'time': '2024-12-23T04:05:00.000000000Z', 'volume': 8, 'open': '1.04396', 'close': '1.04396', 'max': '1.04396', 'min': '1.04396'}, {'time': '2024-12-23T04:06:00.000000000Z', 'volume': 24, 'open': '1.04396', 'close': '1.04398', 'max': '1.04398', 'min': '1.04390'}, {'time': '2024-12-23T04:07:00.000000000Z', 'volume': 19, 'open': '1.04398', 'close': '1.04397', 'max': '1.04400', 'min': '1.04396'}, {'time': '2024-12-23T04:08:00.000000000Z', 'volume': 14, 'open': '1.04398', 'close': '1.04397', 'max': '1.04398', 'min': '1.04397'}, {'time': '2024-12-23T04:09:00.000000000Z', 'volume': 14, 'open': '1.04398', 'close': '1.04394', 'max': '1.04398', 'min': '1.04392'}, {'time': '2024-12-23T04:10:00.000000000Z', 'volume': 25, 'open': '1.04395', 'close': '1.04404', 'max': '1.04404', 'min': '1.04395'}, {'time': '2024-12-23T04:11:00.000000000Z', 'volume': 52, 'open': '1.04404', 'close': '1.04412', 'max': '1.04412', 'min': '1.04398'}, {'time': '2024-12-23T04:12:00.000000000Z', 'volume': 10, 'open': '1.04412', 'close': '1.04412', 'max': '1.04414', 'min': '1.04412'}, {'time': '2024-12-23T04:13:00.000000000Z', 'volume': 12, 'open': '1.04413', 'close': '1.04414', 'max': '1.04416', 'min': '1.04412'}, {'time': '2024-12-23T04:14:00.000000000Z', 'volume': 8, 'open': '1.04414', 'close': '1.04416', 'max': '1.04416', 'min': '1.04414'}]\n\n    2-Minute: [{'time': '2024-12-23T03:46:00.000000000Z', 'volume': 62, 'open': '1.04409', 'close': '1.04400', 'max': '1.04410', 'min': '1.04398'}, {'time': '2024-12-23T03:48:00.000000000Z', 'volume': 82, 'open': '1.04400', 'close': '1.04410', 'max': '1.04410', 'min': '1.04400'}, {'time': '2024-12-23T03:50:00.000000000Z', 'volume': 93, 'open': '1.04410', 'close': '1.04405', 'max': '1.04426', 'min': '1.04404'}, {'time': '2024-12-23T03:52:00.000000000Z', 'volume': 74, 'open': '1.04404', 'close': '1.04401', 'max': '1.04404', 'min': '1.04391'}, {'time': '2024-12-23T03:54:00.000000000Z', 'volume': 40, 'open': '1.04402', 'close': '1.04406', 'max': '1.04410', 'min': '1.04401'}, {'time': '2024-12-23T03:56:00.000000000Z', 'volume': 67, 'open': '1.04404', 'close': '1.04394', 'max': '1.04405', 'min': '1.04393'}, {'time': '2024-12-23T03:58:00.000000000Z', 'volume': 66, 'open': '1.04395', 'close': '1.04395', 'max': '1.04395', 'min': '1.04384'}, {'time': '2024-12-23T04:00:00.000000000Z', 'volume': 82, 'open': '1.04394', 'close': '1.04396', 'max': '1.04400', 'min': '1.04390'}, {'time': '2024-12-23T04:02:00.000000000Z', 'volume': 48, 'open': '1.04397', 'close': '1.04396', 'max': '1.04401', 'min': '1.04394'}, {'time': '2024-12-23T04:04:00.000000000Z', 'volume': 35, 'open': '1.04396', 'close': '1.04396', 'max': '1.04396', 'min': '1.04391'}, {'time': '2024-12-23T04:06:00.000000000Z', 'volume': 43, 'open': '1.04396', 'close': '1.04397', 'max': '1.04400', 'min': '1.04390'}, {'time': '2024-12-23T04:08:00.000000000Z', 'volume': 28, 'open': '1.04398', 'close': '1.04394', 'max': '1.04398', 'min': '1.04392'}, {'time': '2024-12-23T04:10:00.000000000Z', 'volume': 77, 'open': '1.04395', 'close': '1.04412', 'max': '1.04412', 'min': '1.04395'}, {'time': '2024-12-23T04:12:00.000000000Z', 'volume': 22, 'open': '1.04412', 'close': '1.04414', 'max': '1.04416', 'min': '1.04412'}]\n\n    5-Minute: [{'time': '2024-12-23T03:05:00.000000000Z', 'volume': 146, 'open': '1.04402', 'close': '1.04400', 'max': '1.04412', 'min': '1.04392'}, {'time': '2024-12-23T03:10:00.000000000Z', 'volume': 156, 'open': '1.04399', 'close': '1.04407', 'max': '1.04412', 'min': '1.04396'}, {'time': '2024-12-23T03:15:00.000000000Z', 'volume': 138, 'open': '1.04408', 'close': '1.04390', 'max': '1.04408', 'min': '1.04387'}, {'time': '2024-12-23T03:20:00.000000000Z', 'volume': 140, 'open': '1.04392', 'close': '1.04408', 'max': '1.04408', 'min': '1.04392'}, {'time': '2024-12-23T03:25:00.000000000Z', 'volume': 102, 'open': '1.04408', 'close': '1.04402', 'max': '1.04411', 'min': '1.04400'}, {'time': '2024-12-23T03:30:00.000000000Z', 'volume': 117, 'open': '1.04403', 'close': '1.04412', 'max': '1.04412', 'min': '1.04395'}, {'time': '2024-12-23T03:35:00.000000000Z', 'volume': 100, 'open': '1.04412', 'close': '1.04418', 'max': '1.04421', 'min': '1.04410'}, {'time': '2024-12-23T03:40:00.000000000Z', 'volume': 121, 'open': '1.04418', 'close': '1.04406', 'max': '1.04422', 'min': '1.04400'}, {'time': '2024-12-23T03:45:00.000000000Z', 'volume': 162, 'open': '1.04405', 'close': '1.04410', 'max': '1.04412', 'min': '1.04398'}, {'time': '2024-12-23T03:50:00.000000000Z', 'volume': 199, 'open': '1.04410', 'close': '1.04407', 'max': '1.04426', 'min': '1.04391'}, {'time': '2024-12-23T03:55:00.000000000Z', 'volume': 141, 'open': '1.04406', 'close': '1.04395', 'max': '1.04407', 'min': '1.04384'}, {'time': '2024-12-23T04:00:00.000000000Z', 'volume': 157, 'open': '1.04394', 'close': '1.04396', 'max': '1.04401', 'min': '1.04390'}, {'time': '2024-12-23T04:05:00.000000000Z', 'volume': 79, 'open': '1.04396', 'close': '1.04394', 'max': '1.04400', 'min': '1.04390'}, {'time': '2024-12-23T04:10:00.000000000Z', 'volume': 107, 'open': '1.04395', 'close': '1.04416', 'max': '1.04416', 'min': '1.04395'}]"),
#        ("ai","CALL"),
#         (
#               "Analyze the provided candlestick data for the 1-minute, 2-minute, and 5-minute timeframes using CWRV and price action combined Strategy and predict the direction of the next candle using CWRV and price action combined Strategy  for each timeframe. Based on your analysis, respond with CALL if you predict an upward movement across all three timeframes, PUT if you predict a downward movement across all three timeframes, or NEUTRAL if there is no clear direction or if the timeframes do not align. Only provide a signal (CALL or PUT) if all three timeframes show the same direction and you are 100% confident in your prediction. If there is any uncertainty or inconsistency between the timeframes, respond with NEUTRAL. Your response must be strictly in one word: CALL, PUT, or NEUTRAL.\n    Data:\n    1-Minute:[{'time': '2024-12-23T04:03:00.000000000Z', 'volume': 138, 'open': '156.562', 'close': '156.568', 'max': '156.574', 'min': '156.558'}, {'time': '2024-12-23T04:04:00.000000000Z', 'volume': 50, 'open': '156.568', 'close': '156.572', 'max': '156.574', 'min': '156.566'}, {'time': '2024-12-23T04:05:00.000000000Z', 'volume': 50, 'open': '156.573', 'close': '156.568', 'max': '156.574', 'min': '156.568'}, {'time': '2024-12-23T04:06:00.000000000Z', 'volume': 64, 'open': '156.568', 'close': '156.568', 'max': '156.572', 'min': '156.566'}, {'time': '2024-12-23T04:07:00.000000000Z', 'volume': 74, 'open': '156.568', 'close': '156.589', 'max': '156.591', 'min': '156.568'}, {'time': '2024-12-23T04:08:00.000000000Z', 'volume': 118, 'open': '156.588', 'close': '156.591', 'max': '156.594', 'min': '156.584'}, {'time': '2024-12-23T04:09:00.000000000Z', 'volume': 149, 'open': '156.592', 'close': '156.590', 'max': '156.592', 'min': '156.578'}, {'time': '2024-12-23T04:10:00.000000000Z', 'volume': 152, 'open': '156.591', 'close': '156.546', 'max': '156.593', 'min': '156.546'}, {'time': '2024-12-23T04:11:00.000000000Z', 'volume': 87, 'open': '156.546', 'close': '156.555', 'max': '156.564', 'min': '156.545'}, {'time': '2024-12-23T04:12:00.000000000Z', 'volume': 99, 'open': '156.554', 'close': '156.557', 'max': '156.568', 'min': '156.545'}, {'time': '2024-12-23T04:13:00.000000000Z', 'volume': 134, 'open': '156.556', 'close': '156.562', 'max': '156.564', 'min': '156.554'}, {'time': '2024-12-23T04:14:00.000000000Z', 'volume': 144, 'open': '156.562', 'close': '156.562', 'max': '156.570', 'min': '156.556'}, {'time': '2024-12-23T04:15:00.000000000Z', 'volume': 68, 'open': '156.562', 'close': '156.574', 'max': '156.584', 'min': '156.560'}, {'time': '2024-12-23T04:16:00.000000000Z', 'volume': 74, 'open': '156.574', 'close': '156.579', 'max': '156.581', 'min': '156.573'}]\n\n    2-Minute: [{'time': '2024-12-23T03:48:00.000000000Z', 'volume': 234, 'open': '156.523', 'close': '156.506', 'max': '156.524', 'min': '156.501'}, {'time': '2024-12-23T03:50:00.000000000Z', 'volume': 282, 'open': '156.508', 'close': '156.519', 'max': '156.521', 'min': '156.488'}, {'time': '2024-12-23T03:52:00.000000000Z', 'volume': 257, 'open': '156.518', 'close': '156.508', 'max': '156.521', 'min': '156.498'}, {'time': '2024-12-23T03:54:00.000000000Z', 'volume': 239, 'open': '156.509', 'close': '156.502', 'max': '156.518', 'min': '156.498'}, {'time': '2024-12-23T03:56:00.000000000Z', 'volume': 228, 'open': '156.503', 'close': '156.518', 'max': '156.525', 'min': '156.496'}, {'time': '2024-12-23T03:58:00.000000000Z', 'volume': 315, 'open': '156.518', 'close': '156.518', 'max': '156.524', 'min': '156.500'}, {'time': '2024-12-23T04:00:00.000000000Z', 'volume': 347, 'open': '156.521', 'close': '156.548', 'max': '156.551', 'min': '156.521'}, {'time': '2024-12-23T04:02:00.000000000Z', 'volume': 276, 'open': '156.549', 'close': '156.568', 'max': '156.574', 'min': '156.544'}, {'time': '2024-12-23T04:04:00.000000000Z', 'volume': 100, 'open': '156.568', 'close': '156.568', 'max': '156.574', 'min': '156.566'}, {'time': '2024-12-23T04:06:00.000000000Z', 'volume': 138, 'open': '156.568', 'close': '156.589', 'max': '156.591', 'min': '156.566'}, {'time': '2024-12-23T04:08:00.000000000Z', 'volume': 267, 'open': '156.588', 'close': '156.590', 'max': '156.594', 'min': '156.578'}, {'time': '2024-12-23T04:10:00.000000000Z', 'volume': 239, 'open': '156.591', 'close': '156.555', 'max': '156.593', 'min': '156.545'}, {'time': '2024-12-23T04:12:00.000000000Z', 'volume': 233, 'open': '156.554', 'close': '156.562', 'max': '156.568', 'min': '156.545'}, {'time': '2024-12-23T04:14:00.000000000Z', 'volume': 212, 'open': '156.562', 'close': '156.574', 'max': '156.584', 'min': '156.556'}]\n\n    5-Minute: [{'time': '2024-12-23T03:05:00.000000000Z', 'volume': 344, 'open': '156.539', 'close': '156.524', 'max': '156.541', 'min': '156.518'}, {'time': '2024-12-23T03:10:00.000000000Z', 'volume': 348, 'open': '156.525', 'close': '156.558', 'max': '156.564', 'min': '156.517'}, {'time': '2024-12-23T03:15:00.000000000Z', 'volume': 501, 'open': '156.558', 'close': '156.600', 'max': '156.613', 'min': '156.558'}, {'time': '2024-12-23T03:20:00.000000000Z', 'volume': 494, 'open': '156.600', 'close': '156.581', 'max': '156.602', 'min': '156.561'}, {'time': '2024-12-23T03:25:00.000000000Z', 'volume': 501, 'open': '156.582', 'close': '156.593', 'max': '156.599', 'min': '156.566'}, {'time': '2024-12-23T03:30:00.000000000Z', 'volume': 428, 'open': '156.594', 'close': '156.560', 'max': '156.594', 'min': '156.544'}, {'time': '2024-12-23T03:35:00.000000000Z', 'volume': 270, 'open': '156.560', 'close': '156.512', 'max': '156.560', 'min': '156.512'}, {'time': '2024-12-23T03:40:00.000000000Z', 'volume': 569, 'open': '156.511', 'close': '156.535', 'max': '156.552', 'min': '156.498'}, {'time': '2024-12-23T03:45:00.000000000Z', 'volume': 487, 'open': '156.534', 'close': '156.506', 'max': '156.540', 'min': '156.501'}, {'time': '2024-12-23T03:50:00.000000000Z', 'volume': 692, 'open': '156.508', 'close': '156.504', 'max': '156.521', 'min': '156.488'}, {'time': '2024-12-23T03:55:00.000000000Z', 'volume': 629, 'open': '156.504', 'close': '156.518', 'max': '156.525', 'min': '156.496'}, {'time': '2024-12-23T04:00:00.000000000Z', 'volume': 673, 'open': '156.521', 'close': '156.572', 'max': '156.574', 'min': '156.521'}, {'time': '2024-12-23T04:05:00.000000000Z', 'volume': 455, 'open': '156.573', 'close': '156.590', 'max': '156.594', 'min': '156.566'}, {'time': '2024-12-23T04:10:00.000000000Z', 'volume': 616, 'open': '156.591', 'close': '156.562', 'max': '156.593', 'min': '156.545'}]"),
#               ("ai","NEUTRAL"),
#               ("human",signal("EUR_USD",15))
# ]
# ai_msg = llm.invoke(messages)
# print(ai_msg.content)




from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from iqoptionapi.stable_api import IQ_Option
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

app = FastAPI(title="Trading Signal API")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def signal(pair, ofset, google_api_key):
    # Create LLM instance with the provided API key
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-thinking-exp-01-21",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        google_api_key=google_api_key
    )

    headers = {
        'Authorization': 'Bearer 8874b89990ef31aa9fd85b4e3765f222-b4f234623b1f9f383de395ea4910ff6a'
    }

    url_hist1 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M1&count={ofset}'
    url_hist2 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M2&count={ofset}'
    url_hist5 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M5&count={ofset}'

    response1 = requests.get(url_hist1, headers=headers)
    response2 = requests.get(url_hist2, headers=headers)
    response5 = requests.get(url_hist5, headers=headers)
    f1 = response1.json()
    f2 = response2.json()
    f5 = response5.json()
    
    data1 = []
    data2 = []
    data5 = []
    
    for m in f1['candles']:
        if m['complete']:
            f = {
                'time': m['time'],
                'volume': m['volume'],
                'open': m['mid']['o'],
                'close': m['mid']['c'],
                'max': m['mid']['h'],
                'min': m['mid']['l']
            }
            data1.append(f)

    for m in f2['candles']:
        if m['complete']:
            f = {
                'time': m['time'],
                'volume': m['volume'],
                'open': m['mid']['o'],
                'close': m['mid']['c'],
                'max': m['mid']['h'],
                'min': m['mid']['l']
            }
            data2.append(f)

    for m in f5['candles']:
        if m['complete']:
            f = {
                'time': m['time'],
                'volume': m['volume'],
                'open': m['mid']['o'],
                'close': m['mid']['c'],
                'max': m['mid']['h'],
                'min': m['mid']['l']
            }
            data5.append(f)

    messages = [
        (
            "system",
            "Analyze the provided candlestick data for the 1-minute, 2-minute, and 5-minute timeframes using CWRV and price action combined Strategy and predict the direction of the next candle using CWRV and price action combined Strategy  for each timeframe. Based on your analysis, respond with CALL if you predict an upward movement across all three timeframes, PUT if you predict a downward movement across all three timeframes, or NEUTRAL if there is no clear direction or if the timeframes do not align. Only provide a signal (CALL or PUT) if all three timeframes show the same direction and you are 100% confident in your prediction. If there is any uncertainty or inconsistency between the timeframes, respond with NEUTRAL. Your response must be strictly in one word: CALL, PUT, or NEUTRAL.",
        ),
        ("human", "Analyze the provided candlestick data for the 1-minute, 2-minute, and 5-minute timeframes using CWRV and price action combined Strategy and predict the direction of the next candle using CWRV and price action combined Strategy  for each timeframe. Based on your analysis, respond with CALL if you predict an upward movement across all three timeframes, PUT if you predict a downward movement across all three timeframes, or NEUTRAL if there is no clear direction or if the timeframes do not align. Only provide a signal (CALL or PUT) if all three timeframes show the same direction and you are 100% confident in your prediction. If there is any uncertainty or inconsistency between the timeframes, respond with NEUTRAL. Your response must be strictly in one word: CALL, PUT, or NEUTRAL.\n    Data:\n    1-Minute:[{'time': '2024-12-23T03:59:00.000000000Z', 'volume': 39, 'open': '1.04389', 'close': '1.04395', 'max': '1.04395', 'min': '1.04384'}, {'time': '2024-12-23T04:00:00.000000000Z', 'volume': 31, 'open': '1.04394', 'close': '1.04400', 'max': '1.04400', 'min': '1.04390'}, {'time': '2024-12-23T04:01:00.000000000Z', 'volume': 51, 'open': '1.04400', 'close': '1.04396', 'max': '1.04400', 'min': '1.04396'}, {'time': '2024-12-23T04:02:00.000000000Z', 'volume': 26, 'open': '1.04397', 'close': '1.04396', 'max': '1.04398', 'min': '1.04394'}, {'time': '2024-12-23T04:03:00.000000000Z', 'volume': 22, 'open': '1.04396', 'close': '1.04396', 'max': '1.04401', 'min': '1.04396'}, {'time': '2024-12-23T04:04:00.000000000Z', 'volume': 27, 'open': '1.04396', 'close': '1.04396', 'max': '1.04396', 'min': '1.04391'}, {'time': '2024-12-23T04:05:00.000000000Z', 'volume': 8, 'open': '1.04396', 'close': '1.04396', 'max': '1.04396', 'min': '1.04396'}, {'time': '2024-12-23T04:06:00.000000000Z', 'volume': 24, 'open': '1.04396', 'close': '1.04398', 'max': '1.04398', 'min': '1.04390'}, {'time': '2024-12-23T04:07:00.000000000Z', 'volume': 19, 'open': '1.04398', 'close': '1.04397', 'max': '1.04400', 'min': '1.04396'}, {'time': '2024-12-23T04:08:00.000000000Z', 'volume': 14, 'open': '1.04398', 'close': '1.04397', 'max': '1.04398', 'min': '1.04397'}, {'time': '2024-12-23T04:09:00.000000000Z', 'volume': 14, 'open': '1.04398', 'close': '1.04394', 'max': '1.04398', 'min': '1.04392'}, {'time': '2024-12-23T04:10:00.000000000Z', 'volume': 25, 'open': '1.04395', 'close': '1.04404', 'max': '1.04404', 'min': '1.04395'}, {'time': '2024-12-23T04:11:00.000000000Z', 'volume': 52, 'open': '1.04404', 'close': '1.04412', 'max': '1.04412', 'min': '1.04398'}, {'time': '2024-12-23T04:12:00.000000000Z', 'volume': 10, 'open': '1.04412', 'close': '1.04412', 'max': '1.04414', 'min': '1.04412'}]\n\n    2-Minute: [{'time': '2024-12-23T03:44:00.000000000Z', 'volume': 42, 'open': '1.04402', 'close': '1.04410', 'max': '1.04412', 'min': '1.04402'}, {'time': '2024-12-23T03:46:00.000000000Z', 'volume': 62, 'open': '1.04409', 'close': '1.04400', 'max': '1.04410', 'min': '1.04398'}, {'time': '2024-12-23T03:48:00.000000000Z', 'volume': 82, 'open': '1.04400', 'close': '1.04410', 'max': '1.04410', 'min': '1.04400'}, {'time': '2024-12-23T03:50:00.000000000Z', 'volume': 93, 'open': '1.04410', 'close': '1.04405', 'max': '1.04426', 'min': '1.04404'}, {'time': '2024-12-23T03:52:00.000000000Z', 'volume': 74, 'open': '1.04404', 'close': '1.04401', 'max': '1.04404', 'min': '1.04391'}, {'time': '2024-12-23T03:54:00.000000000Z', 'volume': 40, 'open': '1.04402', 'close': '1.04406', 'max': '1.04410', 'min': '1.04401'}, {'time': '2024-12-23T03:56:00.000000000Z', 'volume': 67, 'open': '1.04404', 'close': '1.04394', 'max': '1.04405', 'min': '1.04393'}, {'time': '2024-12-23T03:58:00.000000000Z', 'volume': 66, 'open': '1.04395', 'close': '1.04395', 'max': '1.04395', 'min': '1.04384'}, {'time': '2024-12-23T04:00:00.000000000Z', 'volume': 82, 'open': '1.04394', 'close': '1.04396', 'max': '1.04400', 'min': '1.04390'}, {'time': '2024-12-23T04:02:00.000000000Z', 'volume': 48, 'open': '1.04397', 'close': '1.04396', 'max': '1.04401', 'min': '1.04394'}, {'time': '2024-12-23T04:04:00.000000000Z', 'volume': 35, 'open': '1.04396', 'close': '1.04396', 'max': '1.04396', 'min': '1.04391'}, {'time': '2024-12-23T04:06:00.000000000Z', 'volume': 43, 'open': '1.04396', 'close': '1.04397', 'max': '1.04400', 'min': '1.04390'}, {'time': '2024-12-23T04:08:00.000000000Z', 'volume': 28, 'open': '1.04398', 'close': '1.04394', 'max': '1.04398', 'min': '1.04392'}, {'time': '2024-12-23T04:10:00.000000000Z', 'volume': 77, 'open': '1.04395', 'close': '1.04412', 'max': '1.04412', 'min': '1.04395'}]\n\n    5-Minute: [{'time': '2024-12-23T03:00:00.000000000Z', 'volume': 234, 'open': '1.04406', 'close': '1.04402', 'max': '1.04412', 'min': '1.04386'}, {'time': '2024-12-23T03:05:00.000000000Z', 'volume': 146, 'open': '1.04402', 'close': '1.04400', 'max': '1.04412', 'min': '1.04392'}, {'time': '2024-12-23T03:10:00.000000000Z', 'volume': 156, 'open': '1.04399', 'close': '1.04407', 'max': '1.04412', 'min': '1.04396'}, {'time': '2024-12-23T03:15:00.000000000Z', 'volume': 138, 'open': '1.04408', 'close': '1.04390', 'max': '1.04408', 'min': '1.04387'}, {'time': '2024-12-23T03:20:00.000000000Z', 'volume': 140, 'open': '1.04392', 'close': '1.04408', 'max': '1.04408', 'min': '1.04392'}, {'time': '2024-12-23T03:25:00.000000000Z', 'volume': 102, 'open': '1.04408', 'close': '1.04402', 'max': '1.04411', 'min': '1.04400'}, {'time': '2024-12-23T03:30:00.000000000Z', 'volume': 117, 'open': '1.04403', 'close': '1.04412', 'max': '1.04412', 'min': '1.04395'}, {'time': '2024-12-23T03:35:00.000000000Z', 'volume': 100, 'open': '1.04412', 'close': '1.04418', 'max': '1.04421', 'min': '1.04410'}, {'time': '2024-12-23T03:40:00.000000000Z', 'volume': 121, 'open': '1.04418', 'close': '1.04406', 'max': '1.04422', 'min': '1.04400'}, {'time': '2024-12-23T03:45:00.000000000Z', 'volume': 162, 'open': '1.04405', 'close': '1.04410', 'max': '1.04412', 'min': '1.04398'}, {'time': '2024-12-23T03:50:00.000000000Z', 'volume': 199, 'open': '1.04410', 'close': '1.04407', 'max': '1.04426', 'min': '1.04391'}, {'time': '2024-12-23T03:55:00.000000000Z', 'volume': 141, 'open': '1.04406', 'close': '1.04395', 'max': '1.04407', 'min': '1.04384'}, {'time': '2024-12-23T04:00:00.000000000Z', 'volume': 157, 'open': '1.04394', 'close': '1.04396', 'max': '1.04401', 'min': '1.04390'}, {'time': '2024-12-23T04:05:00.000000000Z', 'volume': 79, 'open': '1.04396', 'close': '1.04394', 'max': '1.04400', 'min': '1.04390'}]"),
     ("ai", "CALL"),
        ("human", f"""Analyze the provided candlestick data for the 1-minute, 2-minute, and 5-minute timeframes using CWRV and price action combined Strategy and predict the direction of the next candle using CWRV and price action combined Strategy  for each timeframe. Based on your analysis, respond with CALL if you predict an upward movement across all three timeframes, PUT if you predict a downward movement across all three timeframes, or NEUTRAL if there is no clear direction or if the timeframes do not align. Only provide a signal (CALL or PUT) if all three timeframes show the same direction and you are 100% confident in your prediction. If there is any uncertainty or inconsistency between the timeframes, respond with NEUTRAL. Your response must be strictly in one word: CALL, PUT, or NEUTRAL.
    Data:
    1-Minute:{data1}

    2-Minute: {data2}

    5-Minute: {data5}
    """),
    ]

    ai_msg = llm.invoke(messages)
    return ai_msg.content

@app.get("/trading-signal", response_model=str, summary="Get Trading Signal")
async def get_trading_signal(
    pair: str = Query(..., description="Trading pair (e.g., EUR_USD)"),
    offset: int = Query(15, description="Number of candles to analyze", ge=1, le=100),
    google_api_key: str = Query(..., description="Google API Key for Gemini AI")
):
    """
    Retrieve a trading signal for a given currency pair.
    
    - **pair**: The trading pair to analyze (e.g., EUR_USD)
    - **offset**: Number of candles to analyze (default: 15, min: 1, max: 100)
    - **google_api_key**: Google API Key for Gemini AI
    
    Returns:
    - CALL: Upward movement predicted
    - PUT: Downward movement predicted
    - NEUTRAL: No clear direction
    """
    try:
        return signal(pair, offset, google_api_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
// Copyright 2021 Optiver Asia Pacific Pty. Ltd.
//
// This file is part of Ready Trader Go.
//
//     Ready Trader Go is free software: you can redistribute it and/or
//     modify it under the terms of the GNU Affero General Public License
//     as published by the Free Software Foundation, either version 3 of
//     the License, or (at your option) any later version.
//
//     Ready Trader Go is distributed in the hope that it will be useful,
//     but WITHOUT ANY WARRANTY; without even the implied warranty of
//     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//     GNU Affero General Public License for more details.
//
//     You should have received a copy of the GNU Affero General Public
//     License along with Ready Trader Go.  If not, see
//     <https://www.gnu.org/licenses/>.
#include <array>
#include <cmath>

#include <boost/asio/io_context.hpp>

#include <ready_trader_go/logging.h>

#include "autotrader.h"

using namespace ReadyTraderGo;

RTG_INLINE_GLOBAL_LOGGER_WITH_CHANNEL(LG_AT, "AUTO")

constexpr int LOT_SIZE = 10;
constexpr int POSITION_LIMIT = 100;
constexpr int TICK_SIZE_IN_CENTS = 100;
constexpr int MIN_BID_NEAREST_TICK = (MINIMUM_BID + TICK_SIZE_IN_CENTS) / TICK_SIZE_IN_CENTS * TICK_SIZE_IN_CENTS;
constexpr int MAX_ASK_NEAREST_TICK = MAXIMUM_ASK / TICK_SIZE_IN_CENTS * TICK_SIZE_IN_CENTS;
constexpr int MAX_HISTORY_LEN = 1000;
constexpr int MIN_HISTORY_LEN = 500;
constexpr int HEDGE_RATIO = 1;
constexpr double ZSCORE_UPPER_THRESHOLD = 0.5;
constexpr double ZSCORE_LOWER_THRESHOLD = -0.5;

AutoTrader::AutoTrader(boost::asio::io_context &context) : BaseAutoTrader(context)
{
}

void AutoTrader::DisconnectHandler()
{
    BaseAutoTrader::DisconnectHandler();
    RLOG(LG_AT, LogLevel::LL_INFO) << "execution connection lost";
}

void AutoTrader::ErrorMessageHandler(unsigned long clientOrderId,
                                     const std::string &errorMessage)
{
    RLOG(LG_AT, LogLevel::LL_INFO) << "error with order " << clientOrderId << ": " << errorMessage;
    if (clientOrderId != 0 && ((mAsks.count(clientOrderId) == 1) || (mBids.count(clientOrderId) == 1)))
    {
        OrderStatusMessageHandler(clientOrderId, 0, 0, 0);
    }
}

void AutoTrader::HedgeFilledMessageHandler(unsigned long clientOrderId,
                                           unsigned long price,
                                           unsigned long volume)
{
    RLOG(LG_AT, LogLevel::LL_INFO) << "hedge order " << clientOrderId << " filled for " << volume
                                   << " lots at $" << price << " average price in cents";
}

void AutoTrader::UpdateHistory(Instrument instrument,
                               const std::array<unsigned long, TOP_LEVEL_COUNT> &askPrices,
                               const std::array<unsigned long, TOP_LEVEL_COUNT> &askVolumes,
                               const std::array<unsigned long, TOP_LEVEL_COUNT> &bidPrices,
                               const std::array<unsigned long, TOP_LEVEL_COUNT> &bidVolumes)
{
    if (instrument == Instrument::FUTURE)
    {
        futureBidPriceHistory.push_back(bidPrices[0]);
        futureAskPriceHistory.push_back(askPrices[0]);
        futureBidVolumeHistory.push_back(askVolumes[0]);
        futureAskVolumeHistory.push_back(bidVolumes[0]);
    }
    if (instrument == Instrument::ETF)
    {
        etfBidPriceHistory.push_back(bidPrices[0]);
        etfAskPriceHistory.push_back(askPrices[0]);
        etfBidVolumeHistory.push_back(bidVolumes[0]);
        etfAskVolumeHistory.push_back(askVolumes[0]);
    }

    for (std::vector<unsigned long> history : {etfBidPriceHistory, etfAskPriceHistory, futureBidPriceHistory, futureAskPriceHistory,
                                               futureBidVolumeHistory, futureAskVolumeHistory, etfBidVolumeHistory, etfAskVolumeHistory})
    {
        if (history.size() > MAX_HISTORY_LEN)
        {
            history.erase(history.begin(), history.begin() + (MAX_HISTORY_LEN - MIN_HISTORY_LEN));
        }
    }
}

void AutoTrader::UpdateSpread(unsigned long sequenceNumber)
{
    if (etfBidPriceHistory.empty() || etfAskPriceHistory.empty() || futureBidPriceHistory.empty() || futureAskPriceHistory.empty())
    {
        return;
    }

    unsigned long eftFutureSpread = etfBidPriceHistory.back() - HEDGE_RATIO * futureAskPriceHistory.back();
    unsigned long futureEtfSpread = futureBidPriceHistory.back() - HEDGE_RATIO * etfAskPriceHistory.back();
    double spread = (double)(eftFutureSpread - futureEtfSpread) / 2;

    if (sequenceNumber == maxSequenceNumber)
    {
        spreadHistory.push_back(spread);
        if (spreadHistory.size() > MAX_HISTORY_LEN)
        {
            spreadHistory.erase(spreadHistory.begin(), spreadHistory.begin() + (MAX_HISTORY_LEN - MIN_HISTORY_LEN));
        }
    }

    if (!spreadHistory.empty())
    {
        spread = spreadHistory.back();
    }

    ++spreadCount;
    double newSpreadMean = spreadMean + (spread - spreadMean) / (double)spreadCount;
    spreadVariance += (spread - spreadMean) * (spread - newSpreadMean);
    spreadMean = newSpreadMean;
    double zscore = (spread - spreadMean) / (sqrt(spreadVariance / (double)spreadCount));

    zscoreHistory.push_back(zscore);
    if (zscoreHistory.size() > MAX_HISTORY_LEN)
    {
        zscoreHistory.erase(zscoreHistory.begin(), zscoreHistory.begin() + (MAX_HISTORY_LEN - MIN_HISTORY_LEN));
    }
}

void AutoTrader::OrderBookMessageHandler(Instrument instrument,
                                         unsigned long sequenceNumber,
                                         const std::array<unsigned long, TOP_LEVEL_COUNT> &askPrices,
                                         const std::array<unsigned long, TOP_LEVEL_COUNT> &askVolumes,
                                         const std::array<unsigned long, TOP_LEVEL_COUNT> &bidPrices,
                                         const std::array<unsigned long, TOP_LEVEL_COUNT> &bidVolumes)
{
    RLOG(LG_AT, LogLevel::LL_INFO) << "order book received for " << instrument << " instrument"
                                   << ": ask prices: " << askPrices[0]
                                   << "; ask volumes: " << askVolumes[0]
                                   << "; bid prices: " << bidPrices[0]
                                   << "; bid volumes: " << bidVolumes[0];

    maxSequenceNumber = std::max(sequenceNumber, maxSequenceNumber);

    if (sequenceNumber == maxSequenceNumber)
    {
        UpdateHistory(instrument, askPrices, askVolumes, bidPrices, bidVolumes);
    }

    UpdateSpread(sequenceNumber);

    unsigned long priceAdjustment = -(mPosition / LOT_SIZE) * TICK_SIZE_IN_CENTS;
    unsigned long newAskPrice = 0, newBidPrice = 0;

    if (!etfAskPriceHistory.empty() && etfAskPriceHistory.back() != 0)
    {
        newAskPrice = etfAskPriceHistory.back() + priceAdjustment;
    }
    if (!etfBidPriceHistory.empty() && etfBidPriceHistory.back() != 0)
    {
        newBidPrice = etfBidPriceHistory.back() + priceAdjustment;
    }

    if (mAskId != 0 && newAskPrice != 0 && newAskPrice != mAskPrice)
    {
        SendCancelOrder(mAskId);
        mAskId = 0;
    }
    if (mBidId != 0 && newBidPrice != 0 && newBidPrice != mBidPrice)
    {
        SendCancelOrder(mBidId);
        mBidId = 0;
    }

    if (mAskId == 0 && newAskPrice != 0 && mPosition > -POSITION_LIMIT)
    {
        if (!zscoreHistory.empty() && zscoreHistory.back() != 0 && zscoreHistory.back() <= ZSCORE_LOWER_THRESHOLD) {
            mAskId = mNextMessageId++;
            mAskPrice = newAskPrice;
            SendInsertOrder(mAskId, Side::SELL, newAskPrice, 15, Lifespan::GOOD_FOR_DAY);
            mAsks.emplace(mAskId);
        }
    }
    if (mBidId == 0 && newBidPrice != 0 && mPosition < POSITION_LIMIT)
    {
        if (!zscoreHistory.empty() && zscoreHistory.back() != 0 && zscoreHistory.back() >= ZSCORE_UPPER_THRESHOLD) {
            mBidId = mNextMessageId++;
            mBidPrice = newBidPrice;
            SendInsertOrder(mBidId, Side::BUY, newBidPrice, 15, Lifespan::GOOD_FOR_DAY);
            mBids.emplace(mBidId);
        }
    }
}

void AutoTrader::OrderFilledMessageHandler(unsigned long clientOrderId,
                                           unsigned long price,
                                           unsigned long volume)
{
    RLOG(LG_AT, LogLevel::LL_INFO) << "order " << clientOrderId << " filled for " << volume
                                   << " lots at $" << price << " cents";
    
    if (mAsks.count(clientOrderId) == 1) // sold an ETF, adjust positions
    {
        mPosition -= (long)volume;
        SendHedgeOrder(mNextMessageId++, Side::BUY, MAX_ASK_NEAREST_TICK, volume);
    }
    else if (mBids.count(clientOrderId) == 1) // bought an ETF, adjust positions
    {
        mPosition += (long)volume;
        SendHedgeOrder(mNextMessageId++, Side::SELL, MIN_BID_NEAREST_TICK, volume);
    }
}

void AutoTrader::OrderStatusMessageHandler(unsigned long clientOrderId,
                                           unsigned long fillVolume,
                                           unsigned long remainingVolume,
                                           signed long fees)
{
    if (remainingVolume == 0)
    {
        if (clientOrderId == mAskId)
        {
            mAskId = 0;
        }
        else if (clientOrderId == mBidId)
        {
            mBidId = 0;
        }

        mAsks.erase(clientOrderId);
        mBids.erase(clientOrderId);
    }
}

void AutoTrader::TradeTicksMessageHandler(Instrument instrument,
                                          unsigned long sequenceNumber,
                                          const std::array<unsigned long, TOP_LEVEL_COUNT> &askPrices,
                                          const std::array<unsigned long, TOP_LEVEL_COUNT> &askVolumes,
                                          const std::array<unsigned long, TOP_LEVEL_COUNT> &bidPrices,
                                          const std::array<unsigned long, TOP_LEVEL_COUNT> &bidVolumes)
{
    RLOG(LG_AT, LogLevel::LL_INFO) << "trade ticks received for " << instrument << " instrument"
                                   << ": ask prices: " << askPrices[0]
                                   << "; ask volumes: " << askVolumes[0]
                                   << "; bid prices: " << bidPrices[0]
                                   << "; bid volumes: " << bidVolumes[0];
}
